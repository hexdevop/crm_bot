from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.db.main import Base


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=22)
    user: Mapped[str] = mapped_column(String(255), default="root")
    password: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extra_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="servers")
    bots = relationship(
        "TgBot", back_populates="server", cascade="all, delete-orphan", lazy="selectin"
    )
