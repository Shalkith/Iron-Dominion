"""Tile model for map grid."""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Tile(Base):
    """Map tile entity representing a grid cell."""

    __tablename__ = "tiles"

    id = Column(Integer, primary_key=True, index=True)
    x = Column(Integer, nullable=False, index=True)
    y = Column(Integer, nullable=False, index=True)

    # Owner (null if unclaimed)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=True, index=True)

    # Resource generation value (randomized on world creation)
    resource_value = Column(Integer, default=1, nullable=False)

    # Relationships
    owner = relationship("Player", back_populates="owned_tiles")

    def __repr__(self) -> str:
        return f"<Tile(id={self.id}, x={self.x}, y={self.y}, owner_id={self.owner_id})>"

    def to_dict(self, include_owner: bool = False) -> dict:
        """Convert tile to dictionary."""
        data = {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "owner_id": self.owner_id,
            "resource_value": self.resource_value,
        }
        if include_owner and self.owner:
            data["owner"] = self.owner.to_dict()
        return data
