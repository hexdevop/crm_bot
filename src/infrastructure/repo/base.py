from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.infrastructure.db.main import Base
from src.infrastructure.cache.manager import CacheManager

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T], cache: CacheManager):
        self.session = session
        self.model = model
        self.cache = cache

    async def get_by_id(self, id: int) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        try:
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except IntegrityError:
            raise

    async def update(self, id: int, **kwargs) -> Optional[T]:
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def delete(self, id: int) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0

    async def get_all_ordered(self, order_by: str = "start") -> List[T]:
        stmt = select(self.model)
        if order_by == "start":
            stmt = stmt.order_by(self.model.id.asc())
        elif order_by == "end":
            stmt = stmt.order_by(self.model.id.desc())
        elif order_by == "random":
            stmt = stmt.order_by(func.rand())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
