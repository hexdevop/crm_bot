from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domain.server import Server
from src.presentation.keyboards.admin.factory import (
    ServerCallbackData,
    BotCallbackData,
)
from src.presentation.keyboards.utils import calc_length, with_pagination


PER_PAGE = 8


def _server_display_name(server: Server) -> str:
    return server.name or f"{server.ip}:{server.port}"


def servers_list(servers: list[Server], count: int, client_id: int, page: int = 1):
    builder = InlineKeyboardBuilder()
    length = calc_length(count, 1, PER_PAGE)
    data = ServerCallbackData(action="view", page=page, client_id=client_id)

    for server in servers:
        data.id = server.id
        label = _server_display_name(server)
        builder.button(text=f"🖥 {label}", callback_data=data.pack())

    data.id = 0
    data.action = "add"
    builder.button(text="➕ Добавить сервер", callback_data=data.pack())

    data.action = "back_to_client"
    builder.button(text="🔙 Назад", callback_data=data.pack())

    sizes = [1] * len(servers) + [1, 1]
    return with_pagination(builder, data, length, page, sizes)


def server_view(data: ServerCallbackData):
    builder = InlineKeyboardBuilder()
    sid, cid = data.id, data.client_id

    bt_data = BotCallbackData(action="list", server_id=sid, client_id=cid)
    builder.button(text="🤖 Боты / Проекты", callback_data=bt_data.pack())

    data.action = "ssh_recheck"
    builder.button(text="🔄 Проверить снова", callback_data=data.pack())

    data.action = "edit_name"
    builder.button(text="✏️ Название", callback_data=data.pack())
    data.action = "edit_ip"
    builder.button(text="✏️ IP", callback_data=data.pack())
    data.action = "edit_port"
    builder.button(text="✏️ Порт", callback_data=data.pack())
    data.action = "edit_user"
    builder.button(text="✏️ Юзер", callback_data=data.pack())
    data.action = "edit_pass"
    builder.button(text="✏️ Пароль", callback_data=data.pack())
    data.action = "edit_extra"
    builder.button(text="✏️ Доп. инфо", callback_data=data.pack())

    data.action = "delete"
    builder.button(text="🗑 Удалить", callback_data=data.pack())
    data.action = "list"
    builder.button(text="🔙 Назад", callback_data=data.pack())

    return builder.adjust(1, 2, 2, 2, 1, 1, 1).as_markup()


def server_delete_confirm(data: ServerCallbackData):
    builder = InlineKeyboardBuilder()
    data.action = "delete_confirm"
    builder.button(text="✅ Да, удалить", callback_data=data.pack())
    data.action = "view"
    builder.button(text="🔙 Отмена", callback_data=data.pack())
    return builder.adjust(1).as_markup()
