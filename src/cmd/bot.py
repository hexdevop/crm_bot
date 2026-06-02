import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from aiogram_i18n import I18nMiddleware

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.config import settings
from src.core.logger import setup_logger

from src.infrastructure.db.main import async_engine, Base
from src.infrastructure.cache.manager import cache_manager
from src.infrastructure.localization.core import CustomFluentCore

from src.presentation.middlewares.db import DbSessionMiddleware
from src.presentation.middlewares.locale import UserLocaleMiddleware
from src.presentation.middlewares.throttling import ThrottlingMiddleware
from src.presentation.handlers.setup import setup_modules
from src.presentation.commands import set_commands
from src.infrastructure.scheduler.tasks import check_all_bot_tokens
from src.presentation.api.setup import setup_api
import uvicorn
from pyngrok import ngrok


async def on_startup(bot: Bot):
    logger = setup_logger()
    bot_info = await bot.get_me()
    settings.username = bot_info.username
    logger.info(f"Запуск бота @{bot_info.username}")

    await set_commands(bot)
    await cache_manager.connect()

    if settings.ENV == "dev":
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Таблицы БД созданы (dev)")

    if settings.USE_WEBHOOK:
        await bot.set_webhook(
            url=settings.webhook_url,
            secret_token=settings.WEBHOOK_SECRET.get_secret_value(),
            allowed_updates=["message", "callback_query", "my_chat_member"],
            drop_pending_updates=settings.SKIP_UPDATES,
        )
    else:
        await bot.delete_webhook(drop_pending_updates=settings.SKIP_UPDATES)


async def on_shutdown(bot: Bot):
    if settings.USE_WEBHOOK:
        await bot.delete_webhook()

    if settings.USE_NGROK:
        ngrok.disconnect(ngrok.get_tunnels()[0].public_url)
        ngrok.kill()

    await cache_manager.close()
    await async_engine.dispose()


async def main():
    setup_logger()

    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML, link_preview_is_disabled=True
        ),
    )

    storage = RedisStorage.from_url(settings.redis_fsm_url)
    dp = Dispatcher(storage=storage)

    dp.update.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.update.middleware(DbSessionMiddleware())

    i18n_core = CustomFluentCore(default_locale="ru", locales=["ru"])
    dp.update.middleware(I18nMiddleware(core=i18n_core))
    dp.update.middleware(UserLocaleMiddleware())

    setup_modules(dp)

    dp.startup.register(on_startup)

    async def _on_shutdown():
        await on_shutdown(bot)

    dp.shutdown.register(_on_shutdown)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_all_bot_tokens,
        trigger="cron",
        hour=0,
        minute=0,
        kwargs={"bot": bot, "admin_ids": settings.ADMIN_IDS},
    )
    scheduler.start()

    if settings.USE_WEBHOOK and settings.USE_NGROK:
        logger = setup_logger()
        if settings.NGROK_AUTHTOKEN:
            ngrok.set_auth_token(settings.NGROK_AUTHTOKEN.get_secret_value())
        connect_kwargs = {"addr": settings.WEB_SERVER_PORT}
        if settings.NGROK_DOMAIN:
            connect_kwargs["domain"] = settings.NGROK_DOMAIN
        tunnel = ngrok.connect(**connect_kwargs)
        settings.WEBHOOK_URL = tunnel.public_url

    if settings.USE_WEBHOOK:
        app = setup_api(bot, dp)
        await dp.emit_startup(bot=bot)
        config = uvicorn.Config(app, host=settings.WEB_SERVER_HOST, port=settings.WEB_SERVER_PORT, loop="asyncio")
        server = uvicorn.Server(config)
        try:
            await server.serve()
        finally:
            await dp.emit_shutdown(bot=bot)
    else:
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
