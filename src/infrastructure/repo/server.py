from sqlalchemy import select, func
from src.infrastructure.repo.base import BaseRepository
from src.domain.server import Server


class ServerRepository(BaseRepository[Server]):

    async def get_by_client(
        self, client_id: int, page: int = 1, per_page: int = 8
    ) -> list[Server]:
        offset = (page - 1) * per_page
        stmt = (
            select(self.model)
            .where(self.model.client_id == client_id)
            .order_by(self.model.id.asc())
            .offset(offset)
            .limit(per_page)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_client(self, client_id: int) -> int:
        stmt = select(func.count(self.model.id)).where(
            self.model.client_id == client_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
