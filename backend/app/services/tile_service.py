"""Tile service for map and territory operations."""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.tile import Tile
from app.models.player import Player
from app.config import get_settings

settings = get_settings()


class TileService:
    """Service for tile-related operations."""

    @staticmethod
    async def get_tile_at(db: AsyncSession, x: int, y: int) -> Optional[Tile]:
        """Get tile at specific coordinates."""
        result = await db.execute(
            select(Tile).where(and_(Tile.x == x, Tile.y == y))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tile_by_id(db: AsyncSession, tile_id: int) -> Optional[Tile]:
        """Get tile by ID."""
        result = await db.execute(
            select(Tile).where(Tile.id == tile_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_player_tiles(db: AsyncSession, player_id: int) -> List[Tile]:
        """Get all tiles owned by a player."""
        result = await db.execute(
            select(Tile).where(Tile.owner_id == player_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_map_data(db: AsyncSession) -> List[Tile]:
        """Get all tiles for map display."""
        result = await db.execute(
            select(Tile).options(selectinload(Tile.owner))
        )
        return result.scalars().all()

    @staticmethod
    async def is_adjacent_to_player_tiles(db: AsyncSession, player_id: int, x: int, y: int) -> bool:
        """Check if coordinates are adjacent to any player-owned tile."""
        player_tiles = await TileService.get_player_tiles(db, player_id)

        for tile in player_tiles:
            if abs(tile.x - x) <= 1 and abs(tile.y - y) <= 1:
                return True
        return False

    @staticmethod
    async def is_adjacent_to_tile(db: AsyncSession, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if two coordinates are adjacent."""
        return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1 and (x1 != x2 or y1 != y2)

    @staticmethod
    async def claim_tile(db: AsyncSession, player_id: int, x: int, y: int) -> Tuple[bool, str, Optional[Tile]]:
        """
        Claim an unowned tile.
        Returns: (success, message, tile)
        """
        # Get tile
        tile = await TileService.get_tile_at(db, x, y)
        if not tile:
            return False, "Tile does not exist", None

        # Check if already owned
        if tile.owner_id is not None:
            return False, "Tile is already claimed", tile

        # Check if player has any tiles (spawn) or is adjacent to owned tile
        player_tiles = await TileService.get_player_tiles(db, player_id)

        if player_tiles:
            # Must be adjacent to existing territory
            is_adjacent = await TileService.is_adjacent_to_player_tiles(db, player_id, x, y)
            if not is_adjacent:
                return False, "Can only claim adjacent tiles", tile

        # Claim the tile
        tile.owner_id = player_id
        await db.commit()
        await db.refresh(tile)

        return True, "Tile claimed successfully", tile

    @staticmethod
    async def generate_map(db: AsyncSession, size: int = None) -> List[Tile]:
        """Generate a new map with random resource values."""
        import random

        if size is None:
            size = settings.map_size

        tiles = []
        for x in range(size):
            for y in range(size):
                # Random resource value between 1 and 5
                resource_value = random.randint(1, 5)
                tile = Tile(x=x, y=y, resource_value=resource_value)
                db.add(tile)
                tiles.append(tile)

        await db.commit()
        return tiles

    @staticmethod
    async def find_spawn_location(db: AsyncSession) -> Optional[Tuple[int, int]]:
        """Find a random unowned tile for player spawn."""
        import random

        result = await db.execute(
            select(Tile).where(Tile.owner_id.is_(None))
        )
        unowned_tiles = result.scalars().all()

        if not unowned_tiles:
            return None

        tile = random.choice(unowned_tiles)
        return (tile.x, tile.y)

    @staticmethod
    async def calculate_player_income(db: AsyncSession, player_id: int) -> int:
        """Calculate total gold income from owned tiles."""
        tiles = await TileService.get_player_tiles(db, player_id)
        return sum(tile.resource_value for tile in tiles)

    @staticmethod
    async def count_player_tiles(db: AsyncSession, player_id: int) -> int:
        """Count tiles owned by player."""
        result = await db.execute(
            select(Tile).where(Tile.owner_id == player_id)
        )
        return len(result.scalars().all())
