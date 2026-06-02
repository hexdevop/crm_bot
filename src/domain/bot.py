from sqlalchemy import BigInteger, String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.db.main import Base
from datetime import datetime


class BotType:
    BOT = "bot"
    PROJECT = "project"


class TgBot(Base):
    __tablename__ = "tg_bots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False
    )
    bot_type: Mapped[str] = mapped_column(String(20), default=BotType.BOT)
    tg_bot_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    token_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extra_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_checked: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    server = relationship("Server", back_populates="bots")
