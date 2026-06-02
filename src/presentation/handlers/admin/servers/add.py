from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.domain.server import Server
from src.infrastructure.repo.server import ServerRepository
from src.presentation.keyboards.admin import reply
from src.presentation.keyboards.admin.factory import ServerCallbackData
from src.presentation.states.admin import ServerState
from src.utils.message import delete_messages

router = Router()


@router.message(L.cancel(), StateFilter(ServerState))
async def cancel_server_add(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    await message.answer(
        text=i18n.get("admin-menu"), reply_markup=reply.main_admin(i18n)
    )


@router.callback_query(ServerCallbackData.filter(F.action == "add"))
async def start_add_server(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    state: FSMContext,
    i18n: I18nContext,
):
    await call.message.delete()
    await state.update_data(client_id=callback_data.client_id)
    msg = await call.message.answer(
        text=i18n.get("server-add-ip"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ServerState.ip)
    await call.answer()


@router.message(ServerState.ip, F.text)
async def get_ip(message: types.Message, state: FSMContext, i18n: I18nContext):
    data = await state.get_data()
    await delete_messages(message, data)
    await state.update_data(ip=message.text.strip())
    msg = await message.answer(
        text=i18n.get("server-add-port"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ServerState.port)


@router.message(ServerState.port, F.text)
async def get_port(message: types.Message, state: FSMContext, i18n: I18nContext):
    data = await state.get_data()
    await delete_messages(message, data)

    skip_text = i18n.get("skip")
    if message.text == skip_text:
        port = 22
    elif message.text.isdigit():
        port = int(message.text)
    else:
        msg = await message.answer(
            text=i18n.get("its-not-digit"),
            reply_markup=reply.skip_and_cancel(i18n),
        )
        await state.update_data(message_id=msg.message_id)
        return

    await state.update_data(port=port)
    msg = await message.answer(
        text=i18n.get("server-add-user"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ServerState.user)


@router.message(ServerState.user, F.text)
async def get_user(message: types.Message, state: FSMContext, i18n: I18nContext):
    data = await state.get_data()
    await delete_messages(message, data)

    skip_text = i18n.get("skip")
    user = "root" if message.text == skip_text else message.text.strip()

    await state.update_data(user=user)
    msg = await message.answer(
        text=i18n.get("server-add-password"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ServerState.password)


@router.message(ServerState.password, F.text)
async def get_password(message: types.Message, state: FSMContext, i18n: I18nContext):
    data = await state.get_data()
    await delete_messages(message, data)

    skip_text = i18n.get("skip")
    password = None if message.text == skip_text else message.text.strip()

    await state.update_data(password=password)
    msg = await message.answer(
        text=i18n.get("server-add-extra"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ServerState.extra_info)


@router.message(ServerState.extra_info, F.text)
async def get_extra(message: types.Message, state: FSMContext, i18n: I18nContext):
    data = await state.get_data()
    await delete_messages(message, data)

    skip_text = i18n.get("skip")
    extra = None if message.text == skip_text else message.text.strip()

    await state.update_data(extra_info=extra)
    msg = await message.answer(
        text=i18n.get("server-add-name"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(ServerState.name)


@router.message(ServerState.name, F.text)
async def get_name_and_save(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    server_repo: ServerRepository,
):
    data = await state.get_data()
    await delete_messages(message, data)

    skip_text = i18n.get("skip")
    name = None if message.text == skip_text else message.text.strip() or None

    server = await server_repo.add(
        Server(
            client_id=data["client_id"],
            ip=data["ip"],
            port=data.get("port", 22),
            user=data.get("user", "root"),
            password=data.get("password"),
            extra_info=data.get("extra_info"),
            name=name,
        )
    )
    await message.answer(
        text=i18n.get("server-added", ip=server.ip),
        reply_markup=reply.main_admin(i18n),
    )
    await state.clear()
