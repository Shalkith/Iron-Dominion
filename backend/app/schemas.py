"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ========== Player Schemas ==========

class PlayerBase(BaseModel):
    """Base player schema."""
    username: str = Field(..., min_length=3, max_length=50)


class PlayerCreate(PlayerBase):
    """Schema for player registration."""
    password: str = Field(..., min_length=6)


class PlayerLogin(PlayerBase):
    """Schema for player login."""
    password: str


class PlayerResponse(PlayerBase):
    """Schema for player response."""
    id: int
    gold: int
    army_size: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlayerPublic(BaseModel):
    """Public player info (for other players)."""
    id: int
    username: str

    class Config:
        from_attributes = True


# ========== Tile Schemas ==========

class TileBase(BaseModel):
    """Base tile schema."""
    x: int
    y: int


class TileResponse(TileBase):
    """Schema for tile response."""
    id: int
    owner_id: Optional[int] = None
    resource_value: int

    class Config:
        from_attributes = True


class TileWithOwner(TileResponse):
    """Tile with owner information."""
    owner: Optional[PlayerPublic] = None


class ClaimTileRequest(BaseModel):
    """Request to claim a tile."""
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)


# ========== Attack Schemas ==========

class AttackRequest(BaseModel):
    """Request to attack a tile."""
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)


class AttackResult(BaseModel):
    """Result of an attack."""
    success: bool
    attacker_won: bool
    message: str
    tile_captured: bool = False


class AttackLogResponse(BaseModel):
    """Attack log entry."""
    id: int
    attacker_id: int
    defender_id: int
    attacker_username: Optional[str]
    defender_username: Optional[str]
    tile_x: int
    tile_y: int
    attacker_army: int
    defender_army: int
    attacker_won: bool
    tile_captured: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Alliance Schemas ==========

class AllianceRequestCreate(BaseModel):
    """Request to create an alliance."""
    to_player_id: int


class AllianceRequestResponse(BaseModel):
    """Alliance request response."""
    id: int
    from_player_id: int
    to_player_id: int
    from_username: Optional[str]
    to_username: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AllianceResponse(BaseModel):
    """Active alliance response."""
    id: int
    player1_id: int
    player2_id: int
    player1_username: Optional[str]
    player2_username: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Game Schemas ==========

class GameTickResponse(BaseModel):
    """Game tick information."""
    tick_number: int
    timestamp: datetime
    gold_generated: int


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    player_id: int
    username: str
    gold: int
    tiles_owned: int
    rank: int
