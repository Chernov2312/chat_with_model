from functools import lru_cache

from gigachat import Chat, GigaChat, Messages

from config import get_settings
from db.models import Message
from schemas.message import MessageRequest


class GigaAI:
    def __init__(self):
        settings = get_settings()
        self.GIGA_KEY = settings.GIGA_KEY
        self.model = "GigaChat-3-Ultra"

    async def send_message_chat(
        self,
        messages: list[Message],
        target_message: MessageRequest,
        system_prompt: str | None = None,
    ):
        async with GigaChat(
            credentials=self.GIGA_KEY,
            verify_ssl_certs=False,
            model=self.model,
        ) as client:
            history = []
            if system_prompt:
                history.append(Messages(role="system", content=system_prompt))
            history.extend(Messages(role=i.role, content=i.content) for i in messages)
            history.append(Messages(role="user", content=target_message.content))
            async for chunk in client.astream(Chat(messages=history, update_interval=0.001)):
                yield chunk.choices[0].delta.content

    async def tokens_count(self, message: str):
        async with GigaChat(
            credentials=self.GIGA_KEY,
            verify_ssl_certs=False,
            model=self.model,
        ) as client:
            res = client.tokens_count(
                input_=[message],
                model=self.model,
            )
            return res[0].tokens


@lru_cache()
def get_giga() -> GigaAI:
    return GigaAI()
