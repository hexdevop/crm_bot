from sqlalchemy import BigInteger, String, DateTime, Index, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.db.main import Base
from datetime import datetime


class UserStatus:
    ACTIVE = "active"
    BLOCKED = "blocked"
    CHAT = "chat"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    language_code: Mapped[str] = mapped_column(String(10), default="ru")
    balance: Mapped[int] = mapped_column(Integer, default=0)
    ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=UserStatus.ACTIVE)
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    __table_args__ = (Index("idx_users_username", "username"),)
