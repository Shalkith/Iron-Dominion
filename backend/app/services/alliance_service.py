"""Alliance service for managing player alliances."""
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.alliance import Alliance, AllianceRequest, AllianceStatus
from app.services.player_service import PlayerService


class AllianceService:
    """Service for alliance-related operations."""

    @staticmethod
    async def send_alliance_request(
        db: AsyncSession,
        from_player_id: int,
        to_player_id: int
    ) -> Tuple[bool, str, Optional[AllianceRequest]]:
        """
        Send an alliance request.
        Returns: (success, message, request)
        """
        # Validate players
        if from_player_id == to_player_id:
            return False, "Cannot ally with yourself", None

        from_player = await PlayerService.get_player_by_id(db, from_player_id)
        to_player = await PlayerService.get_player_by_id(db, to_player_id)

        if not from_player or not to_player:
            return False, "Player not found", None

        # Check if already allied
        existing = await AllianceService.get_alliance_between(db, from_player_id, to_player_id)
        if existing:
            return False, "Already allied with this player", None

        # Check for existing pending request
        result = await db.execute(
            select(AllianceRequest).where(
                ((AllianceRequest.from_player_id == from_player_id) &
                 (AllianceRequest.to_player_id == to_player_id) &
                 (AllianceRequest.status == AllianceStatus.PENDING)) |
                ((AllianceRequest.from_player_id == to_player_id) &
                 (AllianceRequest.to_player_id == from_player_id) &
                 (AllianceRequest.status == AllianceStatus.PENDING))
            )
        )
        if result.scalar_one_or_none():
            return False, "Alliance request already pending", None

        # Create request
        request = AllianceRequest(
            from_player_id=from_player_id,
            to_player_id=to_player_id,
            status=AllianceStatus.PENDING
        )
        db.add(request)
        await db.commit()
        await db.refresh(request)

        return True, "Alliance request sent", request

    @staticmethod
    async def accept_alliance_request(
        db: AsyncSession,
        request_id: int,
        player_id: int
    ) -> Tuple[bool, str, Optional[Alliance]]:
        """
        Accept an alliance request.
        Returns: (success, message, alliance)
        """
        result = await db.execute(
            select(AllianceRequest).where(AllianceRequest.id == request_id)
        )
        request = result.scalar_one_or_none()

        if not request:
            return False, "Alliance request not found", None

        if request.to_player_id != player_id:
            return False, "Cannot accept request not sent to you", None

        if request.status != AllianceStatus.PENDING:
            return False, "Request already responded to", None

        # Update request status
        request.status = AllianceStatus.ACCEPTED
        request.responded_at = datetime.utcnow()

        # Create alliance
        alliance = Alliance(
            player1_id=request.from_player_id,
            player2_id=request.to_player_id
        )
        db.add(alliance)
        await db.commit()
        await db.refresh(alliance)

        return True, "Alliance formed", alliance

    @staticmethod
    async def reject_alliance_request(
        db: AsyncSession,
        request_id: int,
        player_id: int
    ) -> Tuple[bool, str]:
        """Reject an alliance request."""
        result = await db.execute(
            select(AllianceRequest).where(AllianceRequest.id == request_id)
        )
        request = result.scalar_one_or_none()

        if not request:
            return False, "Alliance request not found"

        if request.to_player_id != player_id:
            return False, "Cannot reject request not sent to you"

        if request.status != AllianceStatus.PENDING:
            return False, "Request already responded to"

        request.status = AllianceStatus.REJECTED
        request.responded_at = datetime.utcnow()
        await db.commit()

        return True, "Alliance request rejected"

    @staticmethod
    async def get_alliance_between(
        db: AsyncSession,
        player1_id: int,
        player2_id: int
    ) -> Optional[Alliance]:
        """Get alliance between two players if it exists."""
        result = await db.execute(
            select(Alliance).where(
                ((Alliance.player1_id == player1_id) & (Alliance.player2_id == player2_id)) |
                ((Alliance.player1_id == player2_id) & (Alliance.player2_id == player1_id))
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_player_alliances(db: AsyncSession, player_id: int) -> List[Alliance]:
        """Get all alliances for a player."""
        result = await db.execute(
            select(Alliance)
            .options(selectinload(Alliance.player1), selectinload(Alliance.player2))
            .where(
                (Alliance.player1_id == player_id) | (Alliance.player2_id == player_id)
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_pending_requests(db: AsyncSession, player_id: int) -> List[AllianceRequest]:
        """Get pending alliance requests for a player."""
        result = await db.execute(
            select(AllianceRequest)
            .options(selectinload(AllianceRequest.from_player))
            .where(
                (AllianceRequest.to_player_id == player_id) &
                (AllianceRequest.status == AllianceStatus.PENDING)
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_sent_requests(db: AsyncSession, player_id: int) -> List[AllianceRequest]:
        """Get pending requests sent by a player."""
        result = await db.execute(
            select(AllianceRequest)
            .where(
                (AllianceRequest.from_player_id == player_id) &
                (AllianceRequest.status == AllianceStatus.PENDING)
            )
        )
        return result.scalars().all()
