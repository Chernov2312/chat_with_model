from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dao.basedao import BaseDao
from db.models import User


class UserDao(BaseDao[User]):
    model = User

    @classmethod
    async def get_by_username_or_email(
        cls,
        session: AsyncSession,
        target: str,
    ) -> User | None:
        query = select(cls.model).where(
            or_(cls.model.username == target, cls.model.email == target),
        )
        res = await session.execute(query)
        return res.scalar_one_or_none()
