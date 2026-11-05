import uuid
from typing import List

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dao.basedao import BaseDao
from db.models import Message


class MessageDao(BaseDao):
    model = Message

    @classmethod
    async def get_history(
        cls,
        session: AsyncSession,
        target_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> List[Message]:
        query = (
            select(cls.model)
            .where(and_(Message.session_id == target_id, Message.user_id == user_id))
            .order_by(Message.created_at)
            .limit(50)
        )
        res = await session.execute(query)
        return res.scalars().all()
