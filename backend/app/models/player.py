"""Player model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Player(Base):
    """Player entity representing a game user."""

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Game stats
    gold = Column(Integer, default=100, nullable=False)
    army_size = Column(Integer, default=10, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_attack_at = Column(DateTime, nullable=True)

    # Relationships
    owned_tiles = relationship("Tile", back_populates="owner", lazy="dynamic")
    outgoing_requests = relationship(
        "AllianceRequest",
        foreign_keys="AllianceRequest.from_player_id",
        back_populates="from_player",
        lazy="dynamic"
    )
    incoming_requests = relationship(
        "AllianceRequest",
        foreign_keys="AllianceRequest.to_player_id",
        back_populates="to_player",
        lazy="dynamic"
    )
    alliances_as_player1 = relationship(
        "Alliance",
        foreign_keys="Alliance.player1_id",
        back_populates="player1",
        lazy="dynamic"
    )
    alliances_as_player2 = relationship(
        "Alliance",
        foreign_keys="Alliance.player2_id",
        back_populates="player2",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Player(id={self.id}, username='{self.username}', gold={self.gold}, army={self.army_size})>"

    def to_dict(self) -> dict:
        """Convert player to dictionary (for API responses)."""
        return {
            "id": self.id,
            "username": self.username,
            "gold": self.gold,
            "army_size": self.army_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
