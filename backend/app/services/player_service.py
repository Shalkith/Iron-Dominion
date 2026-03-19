"""Player service for authentication and player management."""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.player import Player
from app.schemas import PlayerCreate, PlayerLogin

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PlayerService:
    """Service for player-related operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def create_player(db: AsyncSession, player_data: PlayerCreate) -> Player:
        """Create a new player."""
        # Check if username exists
        result = await db.execute(
            select(Player).where(Player.username == player_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")

        # Create player
        player = Player(
            username=player_data.username,
            password_hash=PlayerService.hash_password(player_data.password),
            gold=100,  # Starting gold
            army_size=10,  # Starting army
        )
        db.add(player)
        await db.commit()
        await db.refresh(player)
        return player

    @staticmethod
    async def authenticate_player(db: AsyncSession, login_data: PlayerLogin) -> Optional[Player]:
        """Authenticate a player by username and password."""
        result = await db.execute(
            select(Player).where(Player.username == login_data.username)
        )
        player = result.scalar_one_or_none()

        if player and PlayerService.verify_password(login_data.password, player.password_hash):
            return player
        return None

    @staticmethod
    async def get_player_by_id(db: AsyncSession, player_id: int) -> Optional[Player]:
        """Get player by ID."""
        result = await db.execute(
            select(Player).where(Player.id == player_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_player_by_username(db: AsyncSession, username: str) -> Optional[Player]:
        """Get player by username."""
        result = await db.execute(
            select(Player).where(Player.username == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_player_resources(
        db: AsyncSession,
        player_id: int,
        gold_delta: int = 0,
        army_delta: int = 0
    ) -> Optional[Player]:
        """Update player resources."""
        player = await PlayerService.get_player_by_id(db, player_id)
        if not player:
            return None

        player.gold = max(0, player.gold + gold_delta)
        player.army_size = max(0, player.army_size + army_delta)

        await db.commit()
        await db.refresh(player)
        return player
