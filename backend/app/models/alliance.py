"""Alliance models for player alliances."""
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class AllianceStatus(str, enum.Enum):
    """Alliance request status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Alliance(Base):
    """Active alliance between two players."""

    __tablename__ = "alliances"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    player2_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player1 = relationship("Player", foreign_keys=[player1_id], back_populates="alliances_as_player1")
    player2 = relationship("Player", foreign_keys=[player2_id], back_populates="alliances_as_player2")

    def __repr__(self) -> str:
        return f"<Alliance(id={self.id}, p1={self.player1_id}, p2={self.player2_id})>"

    def to_dict(self) -> dict:
        """Convert alliance to dictionary."""
        return {
            "id": self.id,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "player1_username": self.player1.username if self.player1 else None,
            "player2_username": self.player2.username if self.player2 else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AllianceRequest(Base):
    """Pending alliance request between players."""

    __tablename__ = "alliance_requests"

    id = Column(Integer, primary_key=True, index=True)
    from_player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    to_player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    status = Column(String, default=AllianceStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    from_player = relationship("Player", foreign_keys=[from_player_id], back_populates="outgoing_requests")
    to_player = relationship("Player", foreign_keys=[to_player_id], back_populates="incoming_requests")

    def __repr__(self) -> str:
        return f"<AllianceRequest(id={self.id}, from={self.from_player_id}, to={self.to_player_id}, status={self.status})>"

    def to_dict(self) -> dict:
        """Convert alliance request to dictionary."""
        return {
            "id": self.id,
            "from_player_id": self.from_player_id,
            "to_player_id": self.to_player_id,
            "from_username": self.from_player.username if self.from_player else None,
            "to_username": self.to_player.username if self.to_player else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
        }
