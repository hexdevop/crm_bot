from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from src.infrastructure.repo.base import BaseRepository
from src.domain.bot import TgBot
from src.domain.server import Server


class BotRepository(BaseRepository[TgBot]):

    async def get_by_server(
        self, server_id: int, page: int = 1, per_page: int = 8
    ) -> list[TgBot]:
        offset = (page - 1) * per_page
        stmt = (
            select(self.model)
            .where(self.model.server_id == server_id)
            .order_by(self.model.id.asc())
            .offset(offset)
            .limit(per_page)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_server(self, server_id: int) -> int:
        stmt = select(func.count(self.model.id)).where(
            self.model.server_id == server_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_client(self, client_id: int) -> list[TgBot]:
        stmt = (
            select(self.model)
            .join(Server, self.model.server_id == Server.id)
            .where(Server.client_id == client_id)
            .order_by(self.model.id.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_client_with_server(self, client_id: int) -> list[TgBot]:
        stmt = (
            select(self.model)
            .join(Server, self.model.server_id == Server.id)
            .where(Server.client_id == client_id)
            .options(selectinload(self.model.server))
            .order_by(self.model.id.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_client(
        self, client_id: int, query: str, limit: int = 20
    ) -> list[TgBot]:
        stmt = (
            select(self.model)
            .join(Server, self.model.server_id == Server.id)
            .where(
                Server.client_id == client_id,
                or_(
                    self.model.username.ilike(f"%{query}%"),
                    self.model.name.ilike(f"%{query}%"),
                    self.model.token.ilike(f"%{query}%"),
                ),
            )
            .options(selectinload(self.model.server))
            .order_by(self.model.id.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_with_token(self) -> list[TgBot]:
        stmt = (
            select(self.model)
            .where(self.model.token.isnot(None))
            .options(
                selectinload(self.model.server).selectinload(Server.client)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
