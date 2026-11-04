import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Text, desc, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Session(Base):
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
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

    user: Mapped["User | None"] = relationship(back_populates="sessions")

    __table_args__ = (Index("idx_sessions_updated", desc("updated_at")),)
