from src.presentation.keyboards.user.factory import LangCallbackData, SUPPORTED_LOCALES
from src.presentation.keyboards.utils import *
from src.domain.server import Server
from src.domain.bot import TgBot, BotType
from src.presentation.keyboards.admin.factory import ServerCallbackData, BotCallbackData


def user_servers_list(servers: list[Server]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for server in servers:
        data = ServerCallbackData(action="user_view", id=server.id, client_id=0)
        label = server.client_name or server.name or f"{server.ip}:{server.port}"
        builder.button(text=f"🖥 {label}", callback_data=data.pack())
    return builder.adjust(1).as_markup()


def user_server_view_kb(server_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    data = ServerCallbackData(action="user_ssh_recheck", id=server_id, client_id=0)
    builder.button(text="🔄 Проверить снова", callback_data=data.pack())
    data.action = "user_rename"
    builder.button(text="✏️ Моё название", callback_data=data.pack())
    return builder.adjust(1).as_markup()


def user_bots_list(bots: list[TgBot]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for bot in bots:
        icon = "🤖" if bot.bot_type == BotType.BOT else "📦"
        label = f"@{bot.username}" if bot.username else (bot.name or f"ID:{bot.tg_bot_id}")
        srv = bot.server.client_name or bot.server.name or bot.server.ip if bot.server else "?"
        data = BotCallbackData(action="user_view", id=bot.id, server_id=bot.server_id)
        builder.button(text=f"{icon} {label}  [{srv}]", callback_data=data.pack())

    data_search = BotCallbackData(action="user_bot_search", id=0, server_id=0)
    builder.button(text="🔍 Поиск", callback_data=data_search.pack())

    sizes = [1] * len(bots) + [1]
    return builder.adjust(*sizes).as_markup()


def user_bots_search_results(bots: list[TgBot]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for bot in bots:
        icon = "🤖" if bot.bot_type == BotType.BOT else "📦"
        label = f"@{bot.username}" if bot.username else (bot.name or f"ID:{bot.tg_bot_id}")
        srv = bot.server.client_name or bot.server.name or bot.server.ip if bot.server else "?"
        data = BotCallbackData(action="user_view", id=bot.id, server_id=bot.server_id)
        builder.button(text=f"{icon} {label} [{srv}]", callback_data=data.pack())

    back_data = BotCallbackData(action="user_bots_back", id=0, server_id=0)
    builder.button(text="🔙 К списку ботов", callback_data=back_data.pack())

    sizes = [1] * len(bots) + [1]
    return builder.adjust(*sizes).as_markup()


def lang_select(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, name in SUPPORTED_LOCALES.items():
        if code not in i18n.core.available_locales:
            continue
        label = f"✓ {name}" if code == i18n.locale else name
        builder.button(
            text=label,
            callback_data=LangCallbackData(action="set", locale=code).pack(),
        )
    return builder.adjust(2).as_markup()
