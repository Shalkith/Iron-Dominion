"""Combat service for attack resolution."""
from datetime import datetime, timedelta
from typing import Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.player import Player
from app.models.tile import Tile
from app.models.attack_log import AttackLog
from app.models.alliance import Alliance
from app.config import get_settings
from app.services.player_service import PlayerService

settings = get_settings()


class CombatService:
    """Service for combat and attack operations."""

    @staticmethod
    async def can_attack(db: AsyncSession, attacker_id: int, defender_tile: Tile) -> Tuple[bool, str]:
        """Check if attacker can attack a tile."""
        attacker = await PlayerService.get_player_by_id(db, attacker_id)
        if not attacker:
            return False, "Attacker not found"

        # Can't attack unowned tiles
        if defender_tile.owner_id is None:
            return False, "Cannot attack unowned tiles"

        # Can't attack own tiles
        if defender_tile.owner_id == attacker_id:
            return False, "Cannot attack your own tiles"

        # Check alliance - can't attack allies
        is_ally = await CombatService.are_allies(db, attacker_id, defender_tile.owner_id)
        if is_ally:
            return False, "Cannot attack allied players"

        # Check cooldown
        if attacker.last_attack_at:
            cooldown_end = attacker.last_attack_at + timedelta(seconds=settings.attack_cooldown)
            if datetime.utcnow() < cooldown_end:
                remaining = int((cooldown_end - datetime.utcnow()).total_seconds())
                return False, f"Attack on cooldown. Wait {remaining} seconds"

        return True, "Can attack"

    @staticmethod
    async def are_allies(db: AsyncSession, player1_id: int, player2_id: int) -> bool:
        """Check if two players are allies."""
        result = await db.execute(
            select(Alliance).where(
                ((Alliance.player1_id == player1_id) & (Alliance.player2_id == player2_id)) |
                ((Alliance.player1_id == player2_id) & (Alliance.player2_id == player1_id))
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def resolve_attack(
        db: AsyncSession,
        attacker_id: int,
        defender_tile: Tile
    ) -> Tuple[bool, str, Optional[AttackLog]]:
        """
        Resolve an attack between players.
        Returns: (success, message, attack_log)
        """
        # Validate attack
        can_attack, message = await CombatService.can_attack(db, attacker_id, defender_tile)
        if not can_attack:
            return False, message, None

        attacker = await PlayerService.get_player_by_id(db, attacker_id)
        defender = await PlayerService.get_player_by_id(db, defender_tile.owner_id)

        if not defender:
            return False, "Defender not found", None

        # Simple combat resolution: attacker wins if army > defender army
        attacker_won = attacker.army_size > defender.army_size
        tile_captured = False

        # Create attack log
        attack_log = AttackLog(
            attacker_id=attacker_id,
            defender_id=defender.id,
            tile_id=defender_tile.id,
            attacker_army=attacker.army_size,
            defender_army=defender.army_size,
            attacker_won=attacker_won,
            tile_captured=False,  # Will update if captured
        )

        if attacker_won:
            # Transfer tile ownership
            defender_tile.owner_id = attacker_id
            tile_captured = True
            attack_log.tile_captured = True

            # Attacker loses some army (simplified: lose 20%)
            attacker_loss = max(1, defender.army_size // 5)
            attacker.army_size = max(1, attacker.army_size - attacker_loss)

            # Defender loses army
            defender.army_size = max(1, defender.army_size // 2)

            message = f"Attack successful! You captured tile ({defender_tile.x}, {defender_tile.y})"
        else:
            # Attacker loses army
            attacker_loss = max(1, defender.army_size // 3)
            attacker.army_size = max(1, attacker.army_size - attacker_loss)

            message = f"Attack failed! Your army was repelled"

        # Update attack timestamp
        attacker.last_attack_at = datetime.utcnow()

        db.add(attack_log)
        await db.commit()
        await db.refresh(attack_log)

        return True, message, attack_log

    @staticmethod
    async def get_attack_logs_for_player(db: AsyncSession, player_id: int, limit: int = 20):
        """Get recent attack logs for a player (as attacker or defender)."""
        from sqlalchemy import or_

        result = await db.execute(
            select(AttackLog)
            .where(or_(AttackLog.attacker_id == player_id, AttackLog.defender_id == player_id))
            .order_by(AttackLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
