from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.infrastructure.repo.client import ClientRepository
from src.presentation.keyboards.admin import inline, reply
from src.presentation.keyboards.admin.factory import ClientCallbackData
from src.presentation.states.admin import EditClientState
from src.utils.message import delete_messages

router = Router()

_EDIT_PROMPTS = {
    "edit_name": "client-edit-name",
    "edit_username": "client-edit-username",
    "edit_notes": "client-edit-notes",
}

_EDIT_FIELDS = {
    "edit_name": "name",
    "edit_username": "username",
    "edit_notes": "notes",
}


@router.callback_query(ClientCallbackData.filter(F.action.in_(_EDIT_PROMPTS.keys())))
async def start_edit_client(
    call: types.CallbackQuery,
    callback_data: ClientCallbackData,
    state: FSMContext,
    i18n: I18nContext,
):
    action = callback_data.action
    await state.update_data(edit_id=callback_data.id, edit_action=action)
    msg = await call.message.answer(
        text=i18n.get(_EDIT_PROMPTS[action]),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(EditClientState.value)
    await call.answer()


@router.message(EditClientState.value, F.text)
async def process_client_edit(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    data = await state.get_data()
    await delete_messages(message, data)

    action = data["edit_action"]
    field = _EDIT_FIELDS[action]
    entity_id = data["edit_id"]
    skip_text = i18n.get("skip")

    if message.text == skip_text:
        value = None
    elif field == "username":
        value = message.text.strip().lstrip("@") or None
    else:
        value = message.text.strip() or None

    await client_repo.update(entity_id, **{field: value})
    await state.clear()

    client = await client_repo.get_by_id(entity_id)
    cb = ClientCallbackData(action="view", id=entity_id)
    username = f"@{client.username}" if client.username else "—"
    await message.answer(
        text=i18n.get("field-updated") + "\n\n" + i18n.get(
            "client-view",
            name=client.name,
            telegram_id=client.telegram_id,
            username=username,
            servers_count=len(client.servers),
        ),
        reply_markup=inline.client_view(cb),
    )


@router.callback_query(ClientCallbackData.filter(F.action == "notes"))
async def show_notes(
    call: types.CallbackQuery,
    callback_data: ClientCallbackData,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    client = await client_repo.get_by_id(callback_data.id)
    if not client:
        await call.answer(text=i18n.get("client-not-found"), show_alert=True)
        return
    notes_text = client.notes or i18n.get("notes-empty")
    await call.message.edit_text(
        text=i18n.get("client-notes", name=client.name, notes=notes_text),
        reply_markup=inline.client_notes(callback_data),
    )
    await call.answer()


@router.message(L.cancel(), StateFilter(EditClientState))
async def cancel_edit_client(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    await message.answer(
        text=i18n.get("admin-menu"), reply_markup=reply.main_admin(i18n)
    )
