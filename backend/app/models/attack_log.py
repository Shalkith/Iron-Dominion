"""Attack log model for battle records."""
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class AttackLog(Base):
    """Log of attacks between players."""

    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Attacker and defender
    attacker_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    defender_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # Tile that was attacked
    tile_id = Column(Integer, ForeignKey("tiles.id"), nullable=False)

    # Army sizes at time of attack
    attacker_army = Column(Integer, nullable=False)
    defender_army = Column(Integer, nullable=False)

    # Result
    attacker_won = Column(Boolean, nullable=False)
    tile_captured = Column(Boolean, nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    attacker = relationship("Player", foreign_keys=[attacker_id])
    defender = relationship("Player", foreign_keys=[defender_id])
    tile = relationship("Tile")

    def __repr__(self) -> str:
        return f"<AttackLog(id={self.id}, attacker={self.attacker_id}, defender={self.defender_id}, won={self.attacker_won})>"

    def to_dict(self) -> dict:
        """Convert attack log to dictionary."""
        return {
            "id": self.id,
            "attacker_id": self.attacker_id,
            "defender_id": self.defender_id,
            "attacker_username": self.attacker.username if self.attacker else None,
            "defender_username": self.defender.username if self.defender else None,
            "tile_id": self.tile_id,
            "tile_x": self.tile.x if self.tile else None,
            "tile_y": self.tile.y if self.tile else None,
            "attacker_army": self.attacker_army,
            "defender_army": self.defender_army,
            "attacker_won": self.attacker_won,
            "tile_captured": self.tile_captured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
