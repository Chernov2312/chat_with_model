from sqlalchemy import Boolean, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Model(Base):
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    context_window: Mapped[int] = mapped_column(Integer, nullable=False)
    supports_streaming: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
