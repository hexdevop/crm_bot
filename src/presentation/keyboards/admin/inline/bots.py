from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domain.bot import TgBot, BotType
from src.presentation.keyboards.admin.factory import BotCallbackData, ServerCallbackData
from src.presentation.keyboards.utils import calc_length, with_pagination


PER_PAGE = 8


def bots_list(
    bots: list[TgBot], count: int, server_id: int, client_id: int, page: int = 1
):
    builder = InlineKeyboardBuilder()
    length = calc_length(count, 1, PER_PAGE)
    data = BotCallbackData(
        action="view", page=page, server_id=server_id, client_id=client_id
    )

    for bot in bots:
        data.id = bot.id
        icon = "🤖" if bot.bot_type == BotType.BOT else "📦"
        status = "" if bot.token_valid else " ⚠️"
        label = f"@{bot.username}" if bot.username else (bot.name or f"ID:{bot.tg_bot_id}")
        builder.button(text=f"{icon} {label}{status}", callback_data=data.pack())

    data.id = 0
    data.action = "add"
    builder.button(text="➕ Добавить", callback_data=data.pack())

    data.action = "back_to_server"
    builder.button(text="🔙 Назад", callback_data=data.pack())

    sizes = [1] * len(bots) + [1, 1]
    return with_pagination(builder, data, length, page, sizes)


def bot_view(data: BotCallbackData, is_bot: bool = True):
    builder = InlineKeyboardBuilder()

    if is_bot:
        data.action = "refresh_token"
        builder.button(text="🔄 Проверить токен", callback_data=data.pack())
        data.action = "edit_token"
        builder.button(text="✏️ Токен", callback_data=data.pack())
    else:
        data.action = "edit_name"
        builder.button(text="✏️ Имя", callback_data=data.pack())
        data.action = "edit_link"
        builder.button(text="✏️ Ссылка", callback_data=data.pack())

    data.action = "edit_extra"
    builder.button(text="✏️ Доп. инфо", callback_data=data.pack())
    data.action = "edit_comment"
    builder.button(text="✏️ Комментарий", callback_data=data.pack())

    data.action = "delete"
    builder.button(text="🗑 Удалить", callback_data=data.pack())
    data.action = "list"
    builder.button(text="🔙 Назад", callback_data=data.pack())

    return builder.adjust(2, 2, 1, 1).as_markup()


def bot_type_select(server_id: int, client_id: int):
    builder = InlineKeyboardBuilder()
    data = BotCallbackData(action="add_bot", server_id=server_id, client_id=client_id)
    builder.button(text="🤖 Телеграм бот", callback_data=data.pack())
    data.action = "add_project"
    builder.button(text="📦 Проект", callback_data=data.pack())
    data.action = "list"
    builder.button(text="❌ Отмена", callback_data=data.pack())
    return builder.adjust(1).as_markup()


def bot_delete_confirm(data: BotCallbackData):
    builder = InlineKeyboardBuilder()
    data.action = "delete_confirm"
    builder.button(text="✅ Да, удалить", callback_data=data.pack())
    data.action = "view"
    builder.button(text="🔙 Отмена", callback_data=data.pack())
    return builder.adjust(1).as_markup()


def bots_search_results(bots: list[TgBot], server_id: int, client_id: int):
    builder = InlineKeyboardBuilder()
    data = BotCallbackData(action="view", server_id=server_id, client_id=client_id)
    for bot in bots:
        data.id = bot.id
        icon = "🤖" if bot.bot_type == BotType.BOT else "📦"
        label = f"@{bot.username}" if bot.username else (bot.name or f"ID:{bot.tg_bot_id}")
        srv_ip = bot.server.ip if bot.server else "?"
        builder.button(text=f"{icon} {label} [{srv_ip}]", callback_data=data.pack())

    data.id = 0
    data.action = "list"
    builder.button(text="🔙 К списку ботов", callback_data=data.pack())

    sizes = [1] * len(bots) + [1]
    return builder.adjust(*sizes).as_markup()
