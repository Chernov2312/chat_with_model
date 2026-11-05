import uuid
from collections.abc import AsyncIterable

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.sse import EventSourceResponse, ServerSentEvent
from sqlalchemy.ext.asyncio import AsyncSession

from core.ai import GigaAI, get_giga
from core.security import get_id_current_user
from core.utils import get_or_create_gigachat_model
from db.dao.message_dao import Message, MessageDao
from db.dao.session_dao import SessionDao
from db.database import get_session
from schemas.message import MessageHistoryResponse, MessageRequest
from schemas.session import SessionRequest, SessionRespose

session_router = APIRouter(prefix="/api/v1")


@session_router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionRequest,
    user_id: uuid.UUID = Depends(get_id_current_user),
    session_db: AsyncSession = Depends(get_session),
) -> SessionRespose:
    model = await get_or_create_gigachat_model(session=session_db, user_id=user_id)
    data = session_data.model_dump(exclude={"model"})
    data["user_id"] = user_id
    data["model_id"] = model.id
    return await SessionDao.add(session=session_db, data=data)


@session_router.get("/session/info/{session_id}")
async def get_session_info(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_id_current_user),
    session_db: AsyncSession = Depends(get_session),
) -> SessionRespose:
    res = await SessionDao.get_by_id(session=session_db, target_id=session_id, user_id=user_id)
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return res


@session_router.get("/sessions")
async def get_sessions(
    user_id: uuid.UUID = Depends(get_id_current_user),
    session_db: AsyncSession = Depends(get_session),
) -> list[SessionRespose]:
    return await SessionDao.get_all(session=session_db, user_id=user_id)


@session_router.get("/sessions/{session_id}/messages")
async def get_messages_history(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_id_current_user),
    session_db: AsyncSession = Depends(get_session),
) -> MessageHistoryResponse:
    return MessageHistoryResponse(
        messages=(
            await MessageDao.get_history(session=session_db, target_id=session_id, user_id=user_id)
        ),
    )


@session_router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_id_current_user),
    session_db: AsyncSession = Depends(get_session),
):
    if not await SessionDao.delete_by_id(session=session_db, target_id=session_id, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")


@session_router.post("/sessions/{session_id}/messages/stream", response_class=EventSourceResponse)
async def create_message(
    session_id: uuid.UUID,
    message_data: MessageRequest,
    user_id: uuid.UUID = Depends(get_id_current_user),
    giga: GigaAI = Depends(get_giga),
    session_db: AsyncSession = Depends(get_session),
) -> AsyncIterable[ServerSentEvent]:
    chat_session = await SessionDao.get_by_id(
        session=session_db,
        target_id=session_id,
        user_id=user_id,
    )
    if chat_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    messages: list[Message] = await MessageDao.get_history(
        session=session_db,
        target_id=session_id,
        user_id=user_id,
    )
    await MessageDao.add(
        session=session_db,
        data={
            "user_id": user_id,
            "role": "user",
            "content": message_data.content,
            "session_id": session_id,
            "token_count": 0,
        },
    )
    message_id = uuid.uuid4()
    full_message = ""
    async for chunk in giga.send_message_chat(
        messages=messages,
        target_message=message_data,
        system_prompt=chat_session.system_prompt,
    ):
        full_message += chunk
        yield ServerSentEvent(raw_data=chunk, event="token", id=str(message_id))
    token_count = await giga.tokens_count(message=full_message)
    await MessageDao.add(
        session=session_db,
        data={
            "id": message_id,
            "user_id": user_id,
            "role": "assistant",
            "content": full_message,
            "session_id": session_id,
            "token_count": token_count,
        },
    )
    yield ServerSentEvent(raw_data="[DONE]", event="done", id=str(message_id))
