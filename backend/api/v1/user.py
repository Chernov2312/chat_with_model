import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config import RouteTags
from core.security import get_id_current_user
from db.dao.user_dao import User, UserDao
from db.database import get_session
from schemas.user import UserReadResponse, UserUpdateRequest

user_router = APIRouter(prefix="/api/v1/users", tags=[RouteTags.USERS])
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@user_router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(
    session: AsyncSession = Depends(get_session),
    current_user: uuid.UUID = Depends(get_id_current_user),
) -> UserReadResponse:
    current_user_id = current_user[0]
    user = await UserDao.get_by_id(session=session, target_id=current_user_id)
    return user


@user_router.patch("/me", status_code=status.HTTP_200_OK)
async def update_me(
    update_user: UserUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: tuple[uuid.UUID, str] = Depends(get_id_current_user),
) -> UserReadResponse:
    current_user_id = current_user[0]
    try:
        user: User = await UserDao.update_by_id(
            session=session,
            target_id=current_user_id,
            data=update_user.model_dump(exclude_unset=True),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username or email is taken",
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )
    return user
