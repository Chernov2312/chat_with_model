import uuid
from typing import List, Type

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDao[T]:
    model: Type[T]

    @classmethod
    async def add(cls, session: AsyncSession, data: dict) -> T:
        stmt = insert(cls.model).values(**data).returning(cls.model)
        result = await session.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, target_id: uuid.UUID) -> T | None:
        query = select(cls.model).where(cls.model.id == target_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession) -> List[T]:
        query = select(cls.model)
        res = await session.execute(query)
        return list(res.scalars().all())

    @classmethod
    async def update_by_id(
        cls,
        session: AsyncSession,
        target_id: uuid.UUID,
        data: dict,
    ) -> T | None:
        update_data = {k: v for k, v in data.items() if k != "id" and v is not None}
        if not update_data:
            query = select(cls.model).where(cls.model.id == target_id)
            res = await session.execute(query)
            return res.scalar_one_or_none()
        query = (
            update(cls.model)
            .where(cls.model.id == target_id)
            .values(**update_data)
            .returning(cls.model)
            .execution_options(synchronize_session="fetch")
        )
        res = await session.execute(query)
        return res.scalar_one_or_none()

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, target_id: uuid.UUID) -> bool:
        query = delete(cls.model).where(cls.model.id == target_id)
        res = await session.execute(query)
        await session.flush()
        return res.rowcount > 0
