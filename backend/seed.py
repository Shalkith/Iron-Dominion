"""Seed script to generate the game map."""
import asyncio
import random
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal, init_db
from app.models.tile import Tile
from app.config import get_settings

settings = get_settings()


async def seed_map():
    """Generate the game map."""
    print(f"Generating {settings.map_size}x{settings.map_size} map...")

    async with AsyncSessionLocal() as db:
        # Check if map already exists
        from sqlalchemy import select, func
        result = await db.execute(select(func.count()).select_from(Tile))
        count = result.scalar()

        if count > 0:
            print(f"Map already exists with {count} tiles. Skipping generation.")
            return

        tiles = []
        for x in range(settings.map_size):
            for y in range(settings.map_size):
                # Random resource value between 1 and 5
                resource_value = random.randint(1, 5)
                tile = Tile(x=x, y=y, resource_value=resource_value)
                db.add(tile)
                tiles.append(tile)

        await db.commit()
        print(f"Generated {len(tiles)} tiles successfully!")


async def main():
    """Main seed function."""
    print("Initializing database...")
    await init_db()
    await seed_map()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
