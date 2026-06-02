from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.infrastructure.cache.manager import CacheManager
from src.infrastructure.repo.server import ServerRepository
from src.infrastructure.services.ssh import get_or_check_ssh, invalidate_ssh_cache
from src.presentation.keyboards.admin import inline, reply
from src.presentation.keyboards.admin.factory import ServerCallbackData
from src.presentation.states.admin import EditServerState
from src.utils.message import delete_messages

router = Router()

_EDIT_PROMPTS = {
    "edit_name": "server-edit-name",
    "edit_ip": "server-edit-ip",
    "edit_port": "server-edit-port",
    "edit_user": "server-edit-user",
    "edit_pass": "server-edit-pass",
    "edit_extra": "server-edit-extra",
}

_EDIT_FIELDS = {
    "edit_name": "name",
    "edit_ip": "ip",
    "edit_port": "port",
    "edit_user": "user",
    "edit_pass": "password",
    "edit_extra": "extra_info",
}


@router.callback_query(ServerCallbackData.filter(F.action.in_(_EDIT_PROMPTS.keys())))
async def start_edit_server(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    state: FSMContext,
    i18n: I18nContext,
):
    action = callback_data.action
    await state.update_data(
        edit_id=callback_data.id,
        edit_action=action,
        edit_client_id=callback_data.client_id,
    )
    msg = await call.message.answer(
        text=i18n.get(_EDIT_PROMPTS[action]),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(EditServerState.value)
    await call.answer()


@router.message(EditServerState.value, F.text)
async def process_server_edit(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    server_repo: ServerRepository,
    cache_manager: CacheManager,
):
    data = await state.get_data()
    await delete_messages(message, data)

    action = data["edit_action"]
    field = _EDIT_FIELDS[action]
    entity_id = data["edit_id"]
    client_id = data.get("edit_client_id", 0)
    skip_text = i18n.get("skip")

    if message.text == skip_text:
        value = None
    elif field == "port":
        if not message.text.isdigit():
            msg = await message.answer(
                text=i18n.get("its-not-digit"),
                reply_markup=reply.skip_and_cancel(i18n),
            )
            await state.update_data(message_id=msg.message_id)
            return
        value = int(message.text)
    else:
        value = message.text.strip() or None

    await server_repo.update(entity_id, **{field: value})
    await state.clear()

    await invalidate_ssh_cache(entity_id, cache_manager)
    server = await server_repo.get_by_id(entity_id)
    cb = ServerCallbackData(action="view", id=entity_id, client_id=client_id)

    from src.presentation.handlers.admin.servers.main import _server_card
    prefix = i18n.get("field-updated") + "\n\n"
    loading = prefix + _server_card(server, i18n) + "\n\n⏳ " + i18n.get("ssh-checking-inline")
    sent = await message.answer(text=loading, reply_markup=inline.server_view(cb))

    ssh_text = await get_or_check_ssh(
        server.ip, server.port, server.user, server.password,
        entity_id, cache_manager, force=True,
    )
    try:
        await sent.edit_text(
            text=prefix + _server_card(server, i18n) + "\n\n" + ssh_text,
            reply_markup=inline.server_view(cb),
        )
    except Exception:
        pass


@router.message(L.cancel(), StateFilter(EditServerState))
async def cancel_edit_server(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    await message.answer(
        text=i18n.get("admin-menu"), reply_markup=reply.main_admin(i18n)
    )
