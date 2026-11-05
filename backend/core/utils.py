import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Model

GIGACHAT_PROVIDER = "GigaChat"
GIGACHAT_MODEL_NAME = "GigaChat-3-Ultra"
GIGACHAT_CONTEXT_WINDOW = 32_768


async def get_or_create_gigachat_model(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> Model:
    query = select(Model).where(
        Model.user_id == user_id,
        Model.provider == GIGACHAT_PROVIDER,
        Model.display_name == GIGACHAT_MODEL_NAME,
    )
    result = await session.execute(query)
    model = result.scalar_one_or_none()
    if model is not None:
        return model

    model = Model(
        user_id=user_id,
        provider=GIGACHAT_PROVIDER,
        display_name=GIGACHAT_MODEL_NAME,
        context_window=GIGACHAT_CONTEXT_WINDOW,
        supports_streaming=True,
    )
    session.add(model)
    await session.flush()
    return model
