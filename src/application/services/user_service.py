import datetime
from aiogram import types, html
from loguru import logger
from pydantic import BaseModel, ConfigDict
from src.infrastructure.repo.user import UserRepository
from src.domain.user import User, UserStatus


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    full_name: str
    language_code: str

    balance: int

    ref: str | None = None
    status: str
    blocked_at: datetime.datetime | None = None

    @property
    def link(self) -> str:
        if self.username:
            return f"t.me/{self.username}"
        return f"tg://user?id={self.id}"

    @property
    def mention(self) -> str:
        return f'<a href="{self.link}">{self.first_name}</a>'

    @property
    def mention_full(self) -> str:
        return f'<a href="{self.link}">{self.full_name}</a>'


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_or_create_user(
        self,
        from_user: types.User,
        ref: str | None = None,
        is_private: bool = True,
    ) -> UserDTO:
        user = await self.repo.get_by_id(from_user.id)
        if not user:
            initial_status = UserStatus.ACTIVE if is_private else UserStatus.CHAT
            user = User(
                id=from_user.id,
                username=from_user.username,
                first_name=html.quote(from_user.first_name),
                last_name=(
                    html.quote(from_user.last_name) if from_user.last_name else None
                ),
                full_name=from_user.full_name,
                language_code=from_user.language_code,
                ref=ref,
                status=initial_status,
            )
            logger.info(
                f"Пользователь {user.id} зарегистрирован с реф {ref}, статус: {initial_status}"
            )
            user = await self.repo.add(user)
        else:
            updates = {}
            if user.username != from_user.username:
                updates["username"] = from_user.username
            if from_user.first_name and user.first_name != html.quote(from_user.first_name):
                updates["first_name"] = html.quote(from_user.first_name)
            if from_user.last_name and user.last_name != html.quote(from_user.last_name):
                updates["last_name"] = html.quote(from_user.last_name)
            if user.full_name != html.quote(from_user.full_name):
                updates["full_name"] = from_user.full_name

            if is_private:
                if user.status != UserStatus.ACTIVE:
                    updates["status"] = UserStatus.ACTIVE
                    updates["blocked_at"] = None
            else:
                if user.status == UserStatus.BLOCKED:
                    updates["status"] = UserStatus.CHAT

            if updates:
                user = await self.repo.update(from_user.id, **updates)
                logger.info(f"Пользователь {user.id} обновлен: {list(updates.keys())}")

        return UserDTO.model_validate(user)

    async def set_user_status(self, telegram_id: int, status: str):
        updates: dict = {"status": status, "blocked_at": None}
        if status == UserStatus.BLOCKED:
            updates["blocked_at"] = datetime.datetime.now()
        await self.repo.update(telegram_id, **updates)
        logger.info(f"Статус пользователя {telegram_id} → {status}")

    async def update_balance(self, telegram_id: int, amount: int) -> UserDTO:
        user = await self.repo.get_by_id(telegram_id)
        if not user:
            raise ValueError(f"User {telegram_id} not found")

        new_balance = user.balance + amount
        if new_balance < 0:
            raise ValueError(
                f"Insufficient balance for user {telegram_id}: "
                f"balance={user.balance}, change={amount}"
            )

        user = await self.repo.update(telegram_id, balance=new_balance)
        logger.info(f"Баланс пользователя {telegram_id}: {amount:+d} → {user.balance}")
        return UserDTO.model_validate(user)

    async def get_user(self, telegram_id: int) -> UserDTO | None:
        user = await self.repo.get_by_id(telegram_id)
        return UserDTO.model_validate(user) if user else None

    async def get_stats(self):
        now = datetime.datetime.now()
        today_start = datetime.datetime.combine(now.date(), datetime.time.min)
        week_start = today_start - datetime.timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        counts = await self.repo.get_counts_batch(today_start, week_start, month_start)
        languages = await self.repo.get_languages()

        daily_total = await self.repo.get_daily_registrations(month_start, now)
        daily_self = await self.repo.get_daily_self_growth(month_start, now)
        daily_alive = await self.repo.get_daily_alive(month_start, now)
        daily_blocks = await self.repo.get_daily_blocks(month_start, now)

        return {
            "total_users": counts["total"],
            "alive": counts["alive"],
            "chat": counts["chat"],
            "dead": counts["dead"],
            "self_growth": counts["self_growth"],
            "new_today": counts["new_today"],
            "new_week": counts["new_week"],
            "new_month": counts["new_month"],
            "languages": languages,
            "daily_stats": {
                "total": daily_total,
                "self": daily_self,
                "alive": daily_alive,
                "blocks": daily_blocks,
            },
        }
