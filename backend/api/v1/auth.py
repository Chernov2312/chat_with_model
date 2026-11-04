from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from config import RouteTags, settings
from core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from db.dao.user_dao import UserDao
from db.database import get_session
from db.models import User
from schemas.auth import UserLogin, UserRegister, UserResponse

auth_router = APIRouter(prefix="/api/v1/auth", tags=[RouteTags.AUTH])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:

    exist = await UserDao.get_by_username_or_email(session, data.username)
    if not exist:
        exist = await UserDao.get_by_username_or_email(session, data.email)
    if exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username or email already taken",
        )
    hashed_password = get_password_hash(data.password)
    new_user = await UserDao.add(
        session,
        {
            "username": data.username,
            "email": data.email,
            "password": hashed_password,
        },
    )
    await session.commit()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=access_token_expires,
    )
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        access_token=access_token,
    )


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    user: User = await authenticate_user(
        UserLogin(password=form_data.password, username=form_data.username),
        session=session,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        access_token=access_token,
    )
