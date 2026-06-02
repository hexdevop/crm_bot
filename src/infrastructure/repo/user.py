from sqlalchemy import func, select, update, case, or_, and_
from datetime import datetime
from src.infrastructure.repo.base import BaseRepository
from src.domain.user import User, UserStatus


class UserRepository(BaseRepository[User]):
    _LANG_TTL = 604800  # week

    async def get_language(self, user_id: int) -> str | None:
        cache_key = f"user:lang:{user_id}"
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return cached

        stmt = select(self.model.language_code).where(self.model.id == user_id)
        result = await self.session.execute(stmt)
        lang = result.scalar_one_or_none()
        if lang:
            await self.cache.set(cache_key, lang, ttl=self._LANG_TTL)
        return lang

    async def set_language(self, user_id: int, language_code: str) -> None:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == user_id)
            .values(language_code=language_code)
        )
        await self.cache.set(f"user:lang:{user_id}", language_code, ttl=self._LANG_TTL)

    async def get_counts_batch(
        self, today_start: datetime, week_start: datetime, month_start: datetime
    ) -> dict:
        cache_key = f"users:counts_batch:{today_start.date()}"
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return cached

        stmt = select(
            func.sum(case((self.model.status != UserStatus.CHAT, 1), else_=0)).label(
                "total"
            ),
            func.sum(case((self.model.status == UserStatus.ACTIVE, 1), else_=0)).label(
                "alive"
            ),
            func.sum(case((self.model.status == UserStatus.CHAT, 1), else_=0)).label(
                "chat"
            ),
            func.sum(
                case(
                    (
                        and_(
                            self.model.status != UserStatus.ACTIVE,
                            self.model.status != UserStatus.CHAT,
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("dead"),
            func.sum(case((self.model.ref.is_(None), 1), else_=0)).label("self_growth"),
            func.sum(case((self.model.created_at >= today_start, 1), else_=0)).label(
                "new_today"
            ),
            func.sum(case((self.model.created_at >= week_start, 1), else_=0)).label(
                "new_week"
            ),
            func.sum(case((self.model.created_at >= month_start, 1), else_=0)).label(
                "new_month"
            ),
        ).select_from(self.model)

        row = (await self.session.execute(stmt)).one()
        counts = {
            "total": int(row.total or 0),
            "alive": int(row.alive or 0),
            "chat": int(row.chat or 0),
            "dead": int(row.dead or 0),
            "self_growth": int(row.self_growth or 0),
            "new_today": int(row.new_today or 0),
            "new_week": int(row.new_week or 0),
            "new_month": int(row.new_month or 0),
        }
        await self.cache.set(cache_key, counts, ttl=300)
        return counts

    async def get_languages(self):
        stmt = (
            select(self.model.language_code, func.count(self.model.id))
            .group_by(self.model.language_code)
            .order_by(func.count(self.model.id).desc())
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_daily_registrations(self, start_date: datetime, end_date: datetime):
        date_trunc = func.date(self.model.created_at)
        stmt = (
            select(date_trunc, func.count(self.model.id))
            .where(self.model.created_at >= start_date)
            .where(self.model.created_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        return (await self.session.execute(stmt)).all()

    async def get_daily_self_growth(self, start_date: datetime, end_date: datetime):
        date_trunc = func.date(self.model.created_at)
        stmt = (
            select(date_trunc, func.count(self.model.id))
            .where(self.model.created_at >= start_date)
            .where(self.model.created_at <= end_date)
            .where(self.model.ref.is_(None))
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        return (await self.session.execute(stmt)).all()

    async def get_daily_alive(self, start_date: datetime, end_date: datetime):
        date_trunc = func.date(self.model.created_at)
        stmt = (
            select(date_trunc, func.count(self.model.id))
            .where(self.model.created_at >= start_date)
            .where(self.model.created_at <= end_date)
            .where(or_(self.model.status == UserStatus.ACTIVE))
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        return (await self.session.execute(stmt)).all()

    async def get_daily_blocks(self, start_date: datetime, end_date: datetime):
        date_trunc = func.date(self.model.blocked_at)
        stmt = (
            select(date_trunc, func.count(self.model.id))
            .where(self.model.blocked_at >= start_date)
            .where(self.model.blocked_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        return (await self.session.execute(stmt)).all()
