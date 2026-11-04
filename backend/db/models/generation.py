import uuid
from datetime import datetime
from enum import StrEnum
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    desc,
    text, 
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class GenerationStatus(StrEnum):
    pending = "pending"
    streaming = "streaming"
    completed = "completed"
    cancelled = "cancelled"
    failed = "failed"


class Generation(Base):
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_message_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"),
    )
    assistant_message_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"),
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("models.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            GenerationStatus,
            create_constraint=True,
        ),
        nullable=False,
        server_default=GenerationStatus.pending.value,
    )
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    total_tokens: Mapped[int | None] = mapped_column(Integer)
    finish_reason: Mapped[str | None] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    client_disconnected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    __table_args__ = (
        Index(
            "idx_generations_session",
            "session_id",
            desc("started_at"),
        ),
        Index("idx_generations_status", "status"),
    )
