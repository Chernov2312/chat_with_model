from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.auth import auth_router
from api.v1.core import core_router
from api.v1.session import session_router
from api.v1.user import user_router
from db.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI()


app.include_router(core_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(session_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
