from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.domain.client import Client
from src.infrastructure.repo.client import ClientRepository
from src.presentation.keyboards.admin import inline, reply
from src.presentation.keyboards.admin.factory import ClientCallbackData
from src.presentation.states.admin import ClientState
from src.utils.message import delete_messages

router = Router()


@router.message(L.cancel(), StateFilter(ClientState))
async def cancel_client_add(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    await message.answer(
        text=i18n.get("admin-menu"), reply_markup=reply.main_admin(i18n)
    )


@router.callback_query(ClientCallbackData.filter(F.action == "add"))
async def start_add_client(
    call: types.CallbackQuery,
    state: FSMContext,
    i18n: I18nContext,
):
    await call.message.delete()
    msg = await call.message.answer(
        text=i18n.get("client-add-telegram-id"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ClientState.telegram_id)
    await call.answer()


@router.message(ClientState.telegram_id, F.text)
async def get_telegram_id(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    data = await state.get_data()
    await delete_messages(message, data)

    text = message.text.strip()
    if not text.isdigit():
        msg = await message.answer(
            text=i18n.get("its-not-digit"),
            reply_markup=reply.skip_and_cancel(i18n),
        )
        await state.update_data(message_id=msg.message_id)
        return

    telegram_id = int(text)
    existing = await client_repo.get_by_telegram_id(telegram_id)
    if existing:
        msg = await message.answer(
            text=i18n.get("client-already-exists"),
            reply_markup=reply.skip_and_cancel(i18n),
        )
        await state.update_data(message_id=msg.message_id)
        return

    await state.update_data(telegram_id=telegram_id)
    msg = await message.answer(
        text=i18n.get("client-add-name"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ClientState.name)


@router.message(ClientState.name, F.text)
async def get_name(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
):
    data = await state.get_data()
    await delete_messages(message, data)

    await state.update_data(name=message.text.strip())
    msg = await message.answer(
        text=i18n.get("client-add-username"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ClientState.username)


@router.message(ClientState.username, F.text)
async def get_username(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    data = await state.get_data()
    await delete_messages(message, data)

    skip_text = i18n.get("skip")
    username = None if message.text == skip_text else message.text.strip().lstrip("@")

    client = await client_repo.add(
        Client(
            telegram_id=data["telegram_id"],
            name=data["name"],
            username=username,
        )
    )
    await message.answer(
        text=i18n.get("client-added", name=client.name),
        reply_markup=reply.main_admin(i18n),
    )
    await state.clear()
