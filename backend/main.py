from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI()
