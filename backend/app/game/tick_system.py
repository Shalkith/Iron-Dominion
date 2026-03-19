"""Game tick system for resource generation and updates."""
import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.player import Player
from app.models.tile import Tile
from app.services.tile_service import TileService
from app.redis_client import redis_client


class GameTickSystem:
    """Background game tick system."""

    def __init__(self, interval: int = 10):
        """Initialize tick system with interval in seconds."""
        self.interval = interval
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.tick_count = 0

    async def start(self):
        """Start the tick loop."""
        if self.running:
            return

        self.running = True
        self.task = asyncio.create_task(self._tick_loop())
        print(f"[GameTick] Started with {self.interval}s interval")

    async def stop(self):
        """Stop the tick loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("[GameTick] Stopped")

    async def _tick_loop(self):
        """Main tick loop."""
        while self.running:
            try:
                await self._process_tick()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[GameTick] Error: {e}")
                await asyncio.sleep(self.interval)

    async def _process_tick(self):
        """Process a single game tick."""
        self.tick_count += 1
        tick_time = datetime.utcnow()

        async with AsyncSessionLocal() as db:
            try:
                # Get all players
                result = await db.execute(select(Player))
                players = result.scalars().all()

                total_gold_generated = 0

                for player in players:
                    # Calculate income from owned tiles
                    income = await TileService.calculate_player_income(db, player.id)

                    if income > 0:
                        # Update player gold
                        player.gold += income
                        total_gold_generated += income

                await db.commit()

                # Log tick to Redis
                await redis_client.set(
                    "game:last_tick",
                    tick_time.isoformat()
                )
                await redis_client.set(
                    "game:tick_count",
                    str(self.tick_count)
                )
                await redis_client.set(
                    "game:last_gold_generated",
                    str(total_gold_generated)
                )

                # Keep last 100 tick logs in a list
                tick_log = {
                    "tick": self.tick_count,
                    "timestamp": tick_time.isoformat(),
                    "gold_generated": total_gold_generated,
                    "players_online": len(players)
                }
                await redis_client.lpush("game:tick_history", str(tick_log))
                await redis_client.ltrim("game:tick_history", 0, 99)

                print(f"[GameTick #{self.tick_count}] Generated {total_gold_generated} gold for {len(players)} players")

            except Exception as e:
                await db.rollback()
                print(f"[GameTick] Error processing tick: {e}")
                raise

    async def get_status(self) -> dict:
        """Get current tick system status."""
        last_tick = await redis_client.get("game:last_tick")
        tick_count = await redis_client.get("game:tick_count")
        last_gold = await redis_client.get("game:last_gold_generated")

        return {
            "running": self.running,
            "interval": self.interval,
            "tick_count": int(tick_count) if tick_count else 0,
            "last_tick": last_tick,
            "last_gold_generated": int(last_gold) if last_gold else 0,
        }


# Global tick system instance
tick_system = GameTickSystem(interval=10)


async def start_tick_system():
    """Start the game tick system."""
    await tick_system.start()


async def stop_tick_system():
    """Stop the game tick system."""
    await tick_system.stop()
