from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext

from src.infrastructure.cache.manager import CacheManager
from src.infrastructure.repo.server import ServerRepository
from src.infrastructure.repo.client import ClientRepository
from src.infrastructure.services.ssh import get_or_check_ssh, invalidate_ssh_cache
from src.presentation.keyboards.admin import inline
from src.presentation.keyboards.admin.factory import ServerCallbackData

router = Router()


def _server_card(server, i18n: I18nContext) -> str:
    return i18n.get(
        "server-view",
        name=server.name or "—",
        ip=server.ip,
        port=server.port,
        user=server.user,
        password=server.password or "—",
        extra_info=server.extra_info or "—",
        bots_count=len(server.bots),
    )


async def _view_with_auto_ssh(
    message,
    server,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    cache_manager: CacheManager,
    force: bool = False,
) -> None:
    loading = _server_card(server, i18n) + "\n\n⏳ " + i18n.get("ssh-checking-inline")
    try:
        await message.edit_text(text=loading, reply_markup=inline.server_view(callback_data))
    except Exception:
        pass

    ssh_text = await get_or_check_ssh(
        server.ip, server.port, server.user, server.password,
        server.id, cache_manager, force=force,
    )
    full_text = _server_card(server, i18n) + "\n\n" + ssh_text
    try:
        await message.edit_text(text=full_text, reply_markup=inline.server_view(callback_data))
    except Exception:
        pass


@router.callback_query(ServerCallbackData.filter(F.action == "list"))
async def servers_list_cb(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    server_repo: ServerRepository,
    client_repo: ClientRepository,
):
    servers = await server_repo.get_by_client(
        callback_data.client_id, page=callback_data.page
    )
    count = await server_repo.count_by_client(callback_data.client_id)
    await call.message.edit_text(
        text=i18n.get("servers-list" if count > 0 else "servers-empty"),
        reply_markup=inline.servers_list(
            servers, count, callback_data.client_id, page=callback_data.page
        ),
    )
    await call.answer()


@router.callback_query(ServerCallbackData.filter(F.action == "page"))
async def servers_page(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    server_repo: ServerRepository,
):
    servers = await server_repo.get_by_client(
        callback_data.client_id, page=callback_data.page
    )
    count = await server_repo.count_by_client(callback_data.client_id)
    await call.message.edit_text(
        text=i18n.get("servers-list" if count > 0 else "servers-empty"),
        reply_markup=inline.servers_list(
            servers, count, callback_data.client_id, page=callback_data.page
        ),
    )
    await call.answer(text=i18n.get("page", page=callback_data.page))


@router.callback_query(ServerCallbackData.filter(F.action == "back_to_client"))
async def back_to_client(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    from src.presentation.keyboards.admin.factory import ClientCallbackData
    client = await client_repo.get_by_id(callback_data.client_id)
    if not client:
        await call.answer(text=i18n.get("client-not-found"), show_alert=True)
        return
    cl_data = ClientCallbackData(action="view", id=client.id)
    username = f"@{client.username}" if client.username else "—"
    await call.message.edit_text(
        text=i18n.get(
            "client-view",
            name=client.name,
            telegram_id=client.telegram_id,
            username=username,
            servers_count=len(client.servers),
        ),
        reply_markup=inline.client_view(cl_data),
    )
    await call.answer()


@router.callback_query(ServerCallbackData.filter(F.action == "view"))
async def server_view_cb(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    server_repo: ServerRepository,
    cache_manager: CacheManager,
):
    server = await server_repo.get_by_id(callback_data.id)
    if not server:
        await call.answer(text=i18n.get("server-not-found"), show_alert=True)
        return
    await call.answer()
    await _view_with_auto_ssh(
        call.message, server, callback_data, i18n, cache_manager, force=False
    )


@router.callback_query(ServerCallbackData.filter(F.action == "ssh_recheck"))
async def ssh_recheck(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    server_repo: ServerRepository,
    cache_manager: CacheManager,
):
    server = await server_repo.get_by_id(callback_data.id)
    if not server:
        await call.answer(text=i18n.get("server-not-found"), show_alert=True)
        return
    await call.answer()
    await invalidate_ssh_cache(callback_data.id, cache_manager)
    callback_data.action = "view"
    await _view_with_auto_ssh(
        call.message, server, callback_data, i18n, cache_manager, force=True
    )


@router.callback_query(ServerCallbackData.filter(F.action == "delete"))
async def server_delete_ask(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    server_repo: ServerRepository,
):
    server = await server_repo.get_by_id(callback_data.id)
    if not server:
        await call.answer(text=i18n.get("server-not-found"), show_alert=True)
        return
    await call.message.edit_text(
        text=i18n.get("server-delete-confirm", ip=server.ip),
        reply_markup=inline.server_delete_confirm(callback_data),
    )
    await call.answer()


@router.callback_query(ServerCallbackData.filter(F.action == "delete_confirm"))
async def server_delete_confirm(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    server_repo: ServerRepository,
    cache_manager: CacheManager,
):
    await invalidate_ssh_cache(callback_data.id, cache_manager)
    await server_repo.delete(callback_data.id)
    servers = await server_repo.get_by_client(callback_data.client_id, page=1)
    count = await server_repo.count_by_client(callback_data.client_id)
    await call.message.edit_text(
        text=i18n.get("server-deleted") + "\n\n" + i18n.get("servers-list" if count > 0 else "servers-empty"),
        reply_markup=inline.servers_list(servers, count, callback_data.client_id, page=1),
    )
    await call.answer()
