from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from db.database import Base


class User(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255))
