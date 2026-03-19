"""Game mechanics routes (claim, attack, map)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.dependencies import get_current_player
from app.services.tile_service import TileService
from app.services.combat_service import CombatService
from app.services.player_service import PlayerService
from app.schemas import (
    ClaimTileRequest,
    AttackRequest,
    AttackResult,
    TileResponse,
    TileWithOwner,
    AttackLogResponse
)
from app.models.player import Player

router = APIRouter(prefix="/game", tags=["game"])


@router.get("/map", response_model=List[TileResponse])
async def get_map(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Get the entire game map."""
    tiles = await TileService.get_map_data(db)
    return [tile.to_dict() for tile in tiles]


@router.get("/map/with-owners", response_model=List[TileWithOwner])
async def get_map_with_owners(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Get map with owner details."""
    tiles = await TileService.get_map_data(db)
    return [tile.to_dict(include_owner=True) for tile in tiles]


@router.get("/my-tiles", response_model=List[TileResponse])
async def get_my_tiles(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Get all tiles owned by current player."""
    tiles = await TileService.get_player_tiles(db, current_player.id)
    return [tile.to_dict() for tile in tiles]


@router.post("/claim")
async def claim_tile(
    request: ClaimTileRequest,
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Claim an adjacent unowned tile."""
    success, message, tile = await TileService.claim_tile(
        db, current_player.id, request.x, request.y
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "tile": tile.to_dict() if tile else None
    }


@router.post("/attack", response_model=AttackResult)
async def attack_tile(
    request: AttackRequest,
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Attack an enemy tile."""
    # Get target tile
    tile = await TileService.get_tile_at(db, request.x, request.y)
    if not tile:
        raise HTTPException(status_code=404, detail="Tile not found")

    # Resolve attack
    success, message, attack_log = await CombatService.resolve_attack(
        db, current_player.id, tile
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return AttackResult(
        success=True,
        attacker_won=attack_log.attacker_won,
        message=message,
        tile_captured=attack_log.tile_captured
    )


@router.get("/attack-logs")
async def get_attack_logs(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Get attack logs for current player."""
    logs = await CombatService.get_attack_logs_for_player(db, current_player.id)
    return {"logs": [log.to_dict() for log in logs]}


@router.get("/leaderboard")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Get leaderboard sorted by gold."""
    from sqlalchemy import select, func
    from app.models.tile import Tile

    # Get all players with tile counts
    result = await db.execute(
        select(Player, func.count(Tile.id).label("tile_count"))
        .outerjoin(Tile, Player.id == Tile.owner_id)
        .group_by(Player.id)
        .order_by(Player.gold.desc())
    )

    leaderboard = []
    for rank, (player, tile_count) in enumerate(result.all(), 1):
        leaderboard.append({
            "rank": rank,
            "player_id": player.id,
            "username": player.username,
            "gold": player.gold,
            "army_size": player.army_size,
            "tiles_owned": tile_count
        })

    return {"leaderboard": leaderboard}


@router.post("/spawn")
async def spawn_player(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Spawn player at a random location (for new players)."""
    # Check if player already has tiles
    existing_tiles = await TileService.get_player_tiles(db, current_player.id)
    if existing_tiles:
        raise HTTPException(status_code=400, detail="Player already spawned")

    # Find spawn location
    spawn = await TileService.find_spawn_location(db)
    if not spawn:
        raise HTTPException(status_code=500, detail="No available spawn locations")

    x, y = spawn

    # Claim the spawn tile
    success, message, tile = await TileService.claim_tile(db, current_player.id, x, y)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to spawn")

    return {
        "success": True,
        "message": "Spawned successfully",
        "position": {"x": x, "y": y},
        "tile": tile.to_dict()
    }
