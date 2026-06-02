from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from src.core.config import settings
from src.presentation.api.routers.webhook import router as webhook_router
from src.presentation.api.routers.v1 import reg_v1


def setup_api(bot: Bot, dp: Dispatcher) -> FastAPI:
    app = FastAPI(
        title="Bot API", description="REST API for Telegram Bot", version="0.1.0"
    )

    # Сохраняем зависимости в state приложения
    app.state.bot = bot
    app.state.dp = dp

    # Подключаем роутер вебхука (в корень или по заданному пути)
    app.include_router(webhook_router, prefix=settings.WEBHOOK_PATH, tags=["Webhook"])

    # Подключаем остальные роутеры (через пакеты)
    reg_v1(app)

    return app
