"""FastAPI dependencies for authentication and common operations."""
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.player_service import PlayerService
from app.models.player import Player

security = HTTPBearer(auto_error=False)


async def get_current_player(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Player:
    """Get current player from session cookie."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Session ID format: "player_id:{player_id}"
    try:
        if session_id.startswith("player_id:"):
            player_id = int(session_id.split(":")[1])
        else:
            raise HTTPException(status_code=401, detail="Invalid session")
    except (ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid session")

    player = await PlayerService.get_player_by_id(db, player_id)
    if not player:
        raise HTTPException(status_code=401, detail="Player not found")

    return player


async def get_optional_player(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[Player]:
    """Get current player if authenticated, None otherwise."""
    try:
        return await get_current_player(request, db)
    except HTTPException:
        return None
