"""Alliance routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.dependencies import get_current_player
from app.services.alliance_service import AllianceService
from app.services.player_service import PlayerService
from app.schemas import (
    AllianceRequestCreate,
    AllianceRequestResponse,
    AllianceResponse
)
from app.models.player import Player

router = APIRouter(prefix="/alliances", tags=["alliances"])


@router.get("/my", response_model=List[AllianceResponse])
async def get_my_alliances(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Get current player's alliances."""
    alliances = await AllianceService.get_player_alliances(db, current_player.id)
    return [alliance.to_dict() for alliance in alliances]


@router.get("/requests/pending")
async def get_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Get pending alliance requests for current player."""
    requests = await AllianceService.get_pending_requests(db, current_player.id)
    return {
        "incoming": [req.to_dict() for req in requests],
        "outgoing": [req.to_dict() for req in await AllianceService.get_sent_requests(db, current_player.id)]
    }


@router.post("/request")
async def send_alliance_request(
    request: AllianceRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Send an alliance request to another player."""
    # Verify target player exists
    target = await PlayerService.get_player_by_id(db, request.to_player_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target player not found")

    success, message, alliance_request = await AllianceService.send_alliance_request(
        db, current_player.id, request.to_player_id
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "request": alliance_request.to_dict() if alliance_request else None
    }


@router.post("/accept/{request_id}")
async def accept_alliance_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Accept an alliance request."""
    success, message, alliance = await AllianceService.accept_alliance_request(
        db, request_id, current_player.id
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "alliance": alliance.to_dict() if alliance else None
    }


@router.post("/reject/{request_id}")
async def reject_alliance_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Reject an alliance request."""
    success, message = await AllianceService.reject_alliance_request(
        db, request_id, current_player.id
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message
    }


@router.get("/players")
async def get_all_players(
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """Get all players (for finding alliance targets)."""
    from sqlalchemy import select

    result = await db.execute(select(Player))
    players = result.scalars().all()

    return {
        "players": [
            {
                "id": p.id,
                "username": p.username,
                "is_self": p.id == current_player.id
            }
            for p in players
        ]
    }
