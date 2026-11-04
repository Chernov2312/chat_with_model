from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class User(Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
