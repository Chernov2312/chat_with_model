import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dao.basedao import BaseDao
from db.models import Message


class MessageDao(BaseDao):
    model = Message

    @classmethod
    async def get_history(cls, session: AsyncSession, target_id: uuid.UUID) -> List[Message]:
        query = select(cls.model).where(Message.id == uuid).order_by(Message.created_at).limit(50)
        res = await session.execute(query)
        return res.scalars().all()
