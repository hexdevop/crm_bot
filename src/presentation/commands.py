from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeChat,
)

from src.core.config import settings
from src.core.logger import logger


async def set_commands(bot: Bot):
    user_commands = [
        BotCommand(command="start", description="Перезагрузить бота 🔄"),
        BotCommand(command="lang", description="Сменить язык 🌐"),
    ]

    admin_commands = [
        BotCommand(command="admin", description="Панель администратора ⚙️"),
    ]

    chat_commands = [
        BotCommand(command="start", description="Перезагрузить бота"),
    ]

    await bot.set_my_commands(
        commands=user_commands, scope=BotCommandScopeAllPrivateChats()
    )

    await bot.set_my_commands(
        commands=chat_commands, scope=BotCommandScopeAllGroupChats()
    )

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.set_my_commands(
                commands=admin_commands + user_commands,
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except Exception as e:
            logger.error(
                f"Не удалось установить команды для администратора {admin_id}: {e}"
            )
