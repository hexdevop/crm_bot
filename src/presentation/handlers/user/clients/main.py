from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.domain.bot import BotType
from src.infrastructure.cache.manager import CacheManager
from src.infrastructure.repo.client import ClientRepository
from src.infrastructure.repo.server import ServerRepository
from src.infrastructure.repo.bot import BotRepository
from src.infrastructure.services.ssh import get_or_check_ssh, invalidate_ssh_cache
from src.presentation.keyboards.admin.factory import ServerCallbackData, BotCallbackData
from src.presentation.keyboards.user import inline, reply
from src.presentation.states.user import UserServerRenameState
from src.utils.message import delete_messages

router = Router()


def _user_server_card(server, i18n: I18nContext) -> str:
    display = server.client_name or server.name or f"{server.ip}:{server.port}"
    return i18n.get(
        "user-server-view",
        name=display,
        ip=server.ip,
        port=server.port,
        user=server.user,
        password=server.password or "—",
        extra_info=server.extra_info or "—",
    )


async def _update_server_with_ssh(
    msg,
    server,
    i18n: I18nContext,
    cache_manager: CacheManager,
    force: bool = False,
) -> None:
    ssh_text = await get_or_check_ssh(
        server.ip, server.port, server.user, server.password,
        server.id, cache_manager, force=force,
    )
    full_text = _user_server_card(server, i18n) + "\n\n" + ssh_text
    try:
        await msg.edit_text(
            text=full_text,
            reply_markup=inline.user_server_view_kb(server.id),
        )
    except Exception:
        pass


@router.message(L.r.user.my.servers())
async def user_my_servers(
    message: types.Message,
    i18n: I18nContext,
    client_repo: ClientRepository,
    server_repo: ServerRepository,
):
    client = await client_repo.get_by_telegram_id(message.from_user.id)
    if not client:
        await message.answer(text=i18n.get("user-not-client"))
        return
    servers = await server_repo.get_by_client(client.id, page=1, per_page=20)
    if not servers:
        await message.answer(text=i18n.get("user-servers-empty"))
        return
    await message.answer(
        text=i18n.get("user-my-servers"),
        reply_markup=inline.user_servers_list(servers),
    )


@router.message(L.r.user.my.bots())
async def user_my_bots(
    message: types.Message,
    i18n: I18nContext,
    client_repo: ClientRepository,
    bot_repo: BotRepository,
):
    client = await client_repo.get_by_telegram_id(message.from_user.id)
    if not client:
        await message.answer(text=i18n.get("user-not-client"))
        return
    bots = await bot_repo.get_by_client_with_server(client.id)
    if not bots:
        await message.answer(text=i18n.get("user-bots-empty"))
        return
    await message.answer(
        text=i18n.get("user-my-bots"),
        reply_markup=inline.user_bots_list(bots),
    )


@router.callback_query(BotCallbackData.filter(F.action == "user_bots_back"))
async def user_bots_back(
    call: types.CallbackQuery,
    i18n: I18nContext,
    client_repo: ClientRepository,
    bot_repo: BotRepository,
):
    client = await client_repo.get_by_telegram_id(call.from_user.id)
    if not client:
        await call.answer(text=i18n.get("user-not-client"), show_alert=True)
        return
    bots = await bot_repo.get_by_client_with_server(client.id)
    await call.message.edit_text(
        text=i18n.get("user-my-bots"),
        reply_markup=inline.user_bots_list(bots),
    )
    await call.answer()


@router.callback_query(ServerCallbackData.filter(F.action == "user_view"))
async def user_server_view(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    client_repo: ClientRepository,
    server_repo: ServerRepository,
    cache_manager: CacheManager,
):
    client = await client_repo.get_by_telegram_id(call.from_user.id)
    if not client:
        await call.answer(text=i18n.get("user-not-client"), show_alert=True)
        return
    server = await server_repo.get_by_id(callback_data.id)
    if not server or server.client_id != client.id:
        await call.answer(show_alert=True, text="❌ Нет доступа")
        return

    await call.answer()
    sent = await call.message.answer(
        text=_user_server_card(server, i18n) + "\n\n⏳ " + i18n.get("ssh-checking-inline"),
        reply_markup=inline.user_server_view_kb(server.id),
    )
    await _update_server_with_ssh(sent, server, i18n, cache_manager)


@router.callback_query(ServerCallbackData.filter(F.action == "user_ssh_recheck"))
async def user_ssh_recheck(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    i18n: I18nContext,
    client_repo: ClientRepository,
    server_repo: ServerRepository,
    cache_manager: CacheManager,
):
    client = await client_repo.get_by_telegram_id(call.from_user.id)
    if not client:
        await call.answer(text=i18n.get("user-not-client"), show_alert=True)
        return
    server = await server_repo.get_by_id(callback_data.id)
    if not server or server.client_id != client.id:
        await call.answer(show_alert=True, text="❌ Нет доступа")
        return

    await call.answer()
    await invalidate_ssh_cache(callback_data.id, cache_manager)
    # Set loading state (may fail if message already shows loading — ignore)
    try:
        await call.message.edit_text(
            text=_user_server_card(server, i18n) + "\n\n⏳ " + i18n.get("ssh-checking-inline"),
            reply_markup=inline.user_server_view_kb(server.id),
        )
    except Exception:
        pass
    await _update_server_with_ssh(call.message, server, i18n, cache_manager, force=True)


@router.callback_query(ServerCallbackData.filter(F.action == "user_rename"))
async def user_rename_start(
    call: types.CallbackQuery,
    callback_data: ServerCallbackData,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
    server_repo: ServerRepository,
):
    client = await client_repo.get_by_telegram_id(call.from_user.id)
    if not client:
        await call.answer(text=i18n.get("user-not-client"), show_alert=True)
        return
    server = await server_repo.get_by_id(callback_data.id)
    if not server or server.client_id != client.id:
        await call.answer(show_alert=True, text="❌ Нет доступа")
        return

    await state.update_data(rename_server_id=callback_data.id)
    msg = await call.message.answer(
        text=i18n.get("user-server-rename-prompt"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(UserServerRenameState.value)
    await call.answer()


@router.message(UserServerRenameState.value, F.text)
async def user_rename_save(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
    server_repo: ServerRepository,
    cache_manager: CacheManager,
):
    data = await state.get_data()
    await delete_messages(message, data)

    skip_text = i18n.get("skip")
    new_name = None if message.text == skip_text else message.text.strip() or None
    server_id = data["rename_server_id"]

    await server_repo.update(server_id, client_name=new_name)
    await state.clear()

    server = await server_repo.get_by_id(server_id)
    loading = i18n.get("user-server-renamed") + "\n\n" + _user_server_card(server, i18n) + "\n\n⏳ " + i18n.get("ssh-checking-inline")
    sent = await message.answer(
        text=loading,
        reply_markup=inline.user_server_view_kb(server_id),
    )
    await _update_server_with_ssh(sent, server, i18n, cache_manager)


@router.message(L.cancel(), StateFilter(UserServerRenameState))
async def cancel_rename(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    await message.answer(
        text=i18n.get("user-welcome"),
        reply_markup=reply.main_menu(i18n, is_client=True),
    )


@router.callback_query(BotCallbackData.filter(F.action == "user_view"))
async def user_bot_view(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    i18n: I18nContext,
    client_repo: ClientRepository,
    bot_repo: BotRepository,
    server_repo: ServerRepository,
):
    client = await client_repo.get_by_telegram_id(call.from_user.id)
    if not client:
        await call.answer(text=i18n.get("user-not-client"), show_alert=True)
        return
    bot_obj = await bot_repo.get_by_id(callback_data.id)
    if not bot_obj:
        await call.answer(show_alert=True, text="❌ Не найдено")
        return
    server = await server_repo.get_by_id(bot_obj.server_id)
    if not server or server.client_id != client.id:
        await call.answer(show_alert=True, text="❌ Нет доступа")
        return

    srv_label = server.client_name or server.name or server.ip

    if bot_obj.bot_type == BotType.BOT:
        token_status = (
            i18n.get("bot-token-valid") if bot_obj.token_valid else i18n.get("bot-token-invalid")
        )
        await call.message.answer(
            text=i18n.get(
                "user-bot-view",
                name=bot_obj.name or "—",
                username=bot_obj.username or "—",
                bot_id=bot_obj.tg_bot_id or "—",
                token_status=token_status,
                comment=bot_obj.comment or "—",
                extra_info=bot_obj.extra_info or "—",
                server_ip=srv_label,
            )
        )
    else:
        await call.message.answer(
            text=i18n.get(
                "user-project-view",
                name=bot_obj.name or "—",
                link=bot_obj.link or "—",
                comment=bot_obj.comment or "—",
                extra_info=bot_obj.extra_info or "—",
                server_ip=srv_label,
            )
        )
    await call.answer()
