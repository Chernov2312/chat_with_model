import uuid
from typing import List

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dao.basedao import BaseDao
from db.models import Session


class SessionDao(BaseDao):
    model = Session

    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        target_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Session | None:
        query = select(cls.model).where(and_(cls.model.id == target_id, Session.user_id == user_id))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def delete_by_id(
        cls,
        session: AsyncSession,
        target_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        query = delete(cls.model).where(and_(cls.model.id == target_id, Session.user_id == user_id))
        res = await session.execute(query)
        await session.flush()
        return res.rowcount > 0

    @classmethod
    async def get_all(cls, session: AsyncSession, user_id: uuid.UUID) -> List[Session]:
        query = select(cls.model).where(Session.user_id == user_id)
        res = await session.execute(query)
        return list(res.scalars().all())
