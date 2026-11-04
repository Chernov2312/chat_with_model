import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Text, desc, text
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Session(Base):
    model_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("models.id"),
        nullable=False,
    )
    system_prompt: Mapped[str | None] = mapped_column(Text)
    temperature: Mapped[float] = mapped_column(
        nullable=False,
        server_default=text("0.7"),
    )
    max_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("2048"),
    )
    title: Mapped[str | None] = mapped_column(Text)
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    __table_args__ = (Index("idx_sessions_updated", desc("updated_at")),)
