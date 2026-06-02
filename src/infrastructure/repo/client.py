from math import ceil
from sqlalchemy import select, func
from src.infrastructure.repo.base import BaseRepository
from src.domain.client import Client


class ClientRepository(BaseRepository[Client]):

    async def get_by_telegram_id(self, telegram_id: int) -> Client | None:
        stmt = select(self.model).where(self.model.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list(self, page: int = 1, per_page: int = 8) -> list[Client]:
        offset = (page - 1) * per_page
        stmt = (
            select(self.model)
            .order_by(self.model.id.asc())
            .offset(offset)
            .limit(per_page)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count(self.model.id))
        result = await self.session.execute(stmt)
        return result.scalar_one()
