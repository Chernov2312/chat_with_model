import uuid
from collections.abc import AsyncIterable

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.sse import EventSourceResponse, ServerSentEvent
from sqlalchemy.ext.asyncio import AsyncSession

from core.ai import GigaAI, get_giga
from db.dao.message_dao import Message, MessageDao
from db.dao.session_dao import SessionDao
from db.database import get_session
from schemas.message import MessageRequest
from schemas.session import SessionRequest, SessionRespose

session_router = APIRouter()


@session_router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionRequest,
    session_db: AsyncSession = Depends(get_session),
) -> SessionRespose:
    return await SessionDao.add(session=session_db, data=session_data.model_dump())


@session_router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: uuid.UUID,
    session_db: AsyncSession = Depends(get_session),
) -> SessionRespose:
    return await SessionDao.get_by_id(session=session_db, target_id=session_id)


@session_router.get("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    session_db: AsyncSession = Depends(get_session),
):
    if not await SessionDao.delete_by_id(session=session_db, target_id=session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")


@session_router.post("/sessions/{session_id}/messages/stream", response_class=EventSourceResponse)
async def create_message(
    request: Request,
    session_id: uuid.UUID,
    message_data: MessageRequest,
    giga: GigaAI = Depends(get_giga),
    session_db: AsyncSession = Depends(get_session),
) -> AsyncIterable[ServerSentEvent]:
    message_id = uuid.uuid4()
    full_message = ""
    messages: Message = await MessageDao.get_all_by_id(session=session_db)
    async for chunk in giga.send_message_chat(messages=messages, target_message=message_data):
        full_message += chunk
        yield ServerSentEvent(raw_data=chunk, event="token", id=message_id)
    token_count = await giga.tokens_count(input_=[full_message])
    await MessageDao.add(
        session=session_db,
        data={
            "id": message_id,
            "role": message_data.role,
            "session_id": session_id,
            "tokens_count": token_count,
        },
    )
    yield ServerSentEvent(raw_data="[DONE]", event="done", id=message_id)
