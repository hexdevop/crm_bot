from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.infrastructure.repo.client import ClientRepository
from src.presentation.keyboards.admin import inline
from src.presentation.keyboards.admin.factory import ClientCallbackData

router = Router()


@router.message(L.r.admin.clients())
async def clients_menu(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    await state.clear()
    clients = await client_repo.get_list(page=1)
    count = await client_repo.count()
    await message.answer(
        text=i18n.get("clients-menu" if count > 0 else "clients-empty"),
        reply_markup=inline.clients_list(clients, count, page=1),
    )


@router.callback_query(ClientCallbackData.filter(F.action == "main"))
async def clients_list_cb(
    call: types.CallbackQuery,
    callback_data: ClientCallbackData,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    clients = await client_repo.get_list(page=callback_data.page)
    count = await client_repo.count()
    await call.message.edit_text(
        text=i18n.get("clients-menu" if count > 0 else "clients-empty"),
        reply_markup=inline.clients_list(clients, count, page=callback_data.page),
    )
    await call.answer()


@router.callback_query(ClientCallbackData.filter(F.action == "page"))
async def clients_page(
    call: types.CallbackQuery,
    callback_data: ClientCallbackData,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    clients = await client_repo.get_list(page=callback_data.page)
    count = await client_repo.count()
    await call.message.edit_text(
        text=i18n.get("clients-menu" if count > 0 else "clients-empty"),
        reply_markup=inline.clients_list(clients, count, page=callback_data.page),
    )
    await call.answer(text=i18n.get("page", page=callback_data.page))


@router.callback_query(ClientCallbackData.filter(F.action == "view"))
async def client_view_cb(
    call: types.CallbackQuery,
    callback_data: ClientCallbackData,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    client = await client_repo.get_by_id(callback_data.id)
    if not client:
        await call.answer(text=i18n.get("client-not-found"), show_alert=True)
        return

    username = f"@{client.username}" if client.username else "—"
    servers_count = len(client.servers)
    await call.message.edit_text(
        text=i18n.get(
            "client-view",
            name=client.name,
            telegram_id=client.telegram_id,
            username=username,
            servers_count=servers_count,
        ),
        reply_markup=inline.client_view(callback_data),
    )
    await call.answer()


@router.callback_query(ClientCallbackData.filter(F.action == "delete"))
async def client_delete_ask(
    call: types.CallbackQuery,
    callback_data: ClientCallbackData,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    client = await client_repo.get_by_id(callback_data.id)
    if not client:
        await call.answer(text=i18n.get("client-not-found"), show_alert=True)
        return
    await call.message.edit_text(
        text=i18n.get("client-delete-confirm", name=client.name),
        reply_markup=inline.client_delete_confirm(callback_data),
    )
    await call.answer()


@router.callback_query(ClientCallbackData.filter(F.action == "delete_confirm"))
async def client_delete_confirm(
    call: types.CallbackQuery,
    callback_data: ClientCallbackData,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    await client_repo.delete(callback_data.id)
    clients = await client_repo.get_list(page=1)
    count = await client_repo.count()
    await call.message.edit_text(
        text=i18n.get("client-deleted") + "\n\n" + i18n.get("clients-menu" if count > 0 else "clients-empty"),
        reply_markup=inline.clients_list(clients, count, page=1),
    )
    await call.answer()
