from sqlalchemy import Boolean, text
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Model(Base):
    provider: Mapped[str] = mapped_column(nullable=False)
    display_name: Mapped[str] = mapped_column(nullable=False)
    context_window: Mapped[int] = mapped_column(nullable=False)
    supports_streaming: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )