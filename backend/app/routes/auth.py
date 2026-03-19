"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.player_service import PlayerService
from app.schemas import PlayerCreate, PlayerLogin, PlayerResponse

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register", response_model=PlayerResponse)
async def register(
    request: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Register a new player and set session cookie."""
    try:
        player = await PlayerService.create_player(
            db,
            PlayerCreate(username=request.username, password=request.password)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=f"player_id:{player.id}",
        httponly=True,
        max_age=86400 * 7,  # 7 days
        samesite="lax"
    )

    return player


@router.post("/login")
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Login and set session cookie."""
    player = await PlayerService.authenticate_player(
        db,
        PlayerLogin(username=request.username, password=request.password)
    )

    if not player:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=f"player_id:{player.id}",
        httponly=True,
        max_age=86400 * 7,  # 7 days
        samesite="lax"
    )

    return {"message": "Login successful", "player": player.to_dict()}


@router.post("/logout")
async def logout(response: Response):
    """Logout and clear session cookie."""
    response.delete_cookie(key="session_id")
    return {"message": "Logout successful"}


@router.get("/me", response_model=PlayerResponse)
async def get_me(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated player."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        player_id = int(session_id.split(":")[1])
    except (ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid session")

    player = await PlayerService.get_player_by_id(db, player_id)
    if not player:
        raise HTTPException(status_code=401, detail="Player not found")

    return player
