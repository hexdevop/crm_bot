from aiogram.filters import BaseFilter
from aiogram.types import Message
from src.core.config import settings


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return message.from_user.id in settings.ADMIN_IDS
