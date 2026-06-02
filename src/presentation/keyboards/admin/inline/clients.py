from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.domain.client import Client
from src.presentation.keyboards.admin.factory import ClientCallbackData, ServerCallbackData
from src.presentation.keyboards.utils import calc_length, with_pagination


PER_PAGE = 8


def clients_list(clients: list[Client], count: int, page: int = 1):
    builder = InlineKeyboardBuilder()
    length = calc_length(count, 1, PER_PAGE)
    data = ClientCallbackData(action="view", page=page)

    for client in clients:
        data.id = client.id
        label = client.name
        if client.username:
            label += f" @{client.username}"
        builder.button(text=label, callback_data=data.pack())

    data.id = 0
    data.action = "add"
    builder.button(text="➕ Добавить клиента", callback_data=data.pack())

    sizes = [1] * len(clients) + [1]
    return with_pagination(builder, data, length, page, sizes)


def client_view(data: ClientCallbackData):
    builder = InlineKeyboardBuilder()
    cid = data.id

    sv_data = ServerCallbackData(action="list", client_id=cid)
    builder.button(text="🖥 Серверы", callback_data=sv_data.pack())

    data.action = "notes"
    builder.button(text="📝 Заметки", callback_data=data.pack())

    data.action = "edit_name"
    builder.button(text="✏️ Имя", callback_data=data.pack())

    data.action = "edit_username"
    builder.button(text="✏️ Username", callback_data=data.pack())

    data.action = "delete"
    builder.button(text="🗑 Удалить", callback_data=data.pack())

    data.action = "main"
    builder.button(text="🔙 Назад", callback_data=data.pack())

    return builder.adjust(1, 1, 2, 1, 1).as_markup()


def client_notes(data: ClientCallbackData):
    builder = InlineKeyboardBuilder()
    data.action = "edit_notes"
    builder.button(text="✏️ Изменить заметки", callback_data=data.pack())
    data.action = "view"
    builder.button(text="🔙 Назад", callback_data=data.pack())
    return builder.adjust(1).as_markup()


def client_delete_confirm(data: ClientCallbackData):
    builder = InlineKeyboardBuilder()
    data.action = "delete_confirm"
    builder.button(text="✅ Да, удалить", callback_data=data.pack())
    data.action = "view"
    builder.button(text="🔙 Отмена", callback_data=data.pack())
    return builder.adjust(1).as_markup()
