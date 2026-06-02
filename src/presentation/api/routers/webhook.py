from fastapi import APIRouter, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from src.core.config import settings

router = APIRouter()


@router.post("")
async def handle_webhook(request: Request):
    bot: Bot = request.app.state.bot
    dp: Dispatcher = request.app.state.dp

    # Проверка секретного токена
    token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if token != settings.WEBHOOK_SECRET.get_secret_value():
        return Response(content="Invalid secret token", status_code=403)

    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"status": "ok"}
