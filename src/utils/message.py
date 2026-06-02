from aiogram import types, Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError


class Plug:
    message_id = 000


async def delete_messages(
    event: types.Message | types.CallbackQuery,
    data: dict = None,
    user_id: int = None,
):
    try:
        if isinstance(event, types.Message):
            message_ids = [event.message_id]
        else:
            message_ids = [event.message.message_id]
        if data:
            message_ids += data.get("message_ids", [])
            if "message_id" in data.keys():
                message_ids.append(data.get("message_id"))
        await event.bot.delete_messages(
            chat_id=user_id or event.from_user.id, message_ids=message_ids
        )
    except TelegramBadRequest:
        pass


async def send_message(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup: types.ReplyKeyboardMarkup | types.InlineKeyboardMarkup = None,
):
    try:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )
    except (TelegramBadRequest, TelegramForbiddenError):
        return Plug()
