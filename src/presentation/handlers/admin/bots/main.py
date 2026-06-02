from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from aiogram.exceptions import TelegramUnauthorizedError

from src.domain.bot import BotType
from src.infrastructure.repo.bot import BotRepository
from src.infrastructure.repo.server import ServerRepository
from src.presentation.keyboards.admin import inline
from src.presentation.keyboards.admin.factory import BotCallbackData

router = Router()


@router.callback_query(BotCallbackData.filter(F.action == "list"))
async def bots_list_cb(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    bots = await bot_repo.get_by_server(
        callback_data.server_id, page=callback_data.page
    )
    count = await bot_repo.count_by_server(callback_data.server_id)
    await call.message.edit_text(
        text=i18n.get("bots-list" if count > 0 else "bots-empty"),
        reply_markup=inline.bots_list(
            bots,
            count,
            callback_data.server_id,
            callback_data.client_id,
            page=callback_data.page,
        ),
    )
    await call.answer()


@router.callback_query(BotCallbackData.filter(F.action == "page"))
async def bots_page(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    bots = await bot_repo.get_by_server(
        callback_data.server_id, page=callback_data.page
    )
    count = await bot_repo.count_by_server(callback_data.server_id)
    await call.message.edit_text(
        text=i18n.get("bots-list" if count > 0 else "bots-empty"),
        reply_markup=inline.bots_list(
            bots,
            count,
            callback_data.server_id,
            callback_data.client_id,
            page=callback_data.page,
        ),
    )
    await call.answer(text=i18n.get("page", page=callback_data.page))


@router.callback_query(BotCallbackData.filter(F.action == "back_to_server"))
async def back_to_server(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    i18n: I18nContext,
    server_repo: ServerRepository,
):
    from src.presentation.keyboards.admin.factory import ServerCallbackData
    server = await server_repo.get_by_id(callback_data.server_id)
    if not server:
        await call.answer(text=i18n.get("server-not-found"), show_alert=True)
        return

    sv_data = ServerCallbackData(
        action="view", id=server.id, client_id=callback_data.client_id
    )
    password = server.password or "—"
    extra = server.extra_info or "—"
    await call.message.edit_text(
        text=i18n.get(
            "server-view",
            ip=server.ip,
            port=server.port,
            user=server.user,
            password=password,
            extra_info=extra,
            bots_count=len(server.bots),
        ),
        reply_markup=inline.server_view(sv_data),
    )
    await call.answer()


@router.callback_query(BotCallbackData.filter(F.action == "view"))
async def bot_view_cb(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    bot_obj = await bot_repo.get_by_id(callback_data.id)
    if not bot_obj:
        await call.answer(text=i18n.get("bot-not-found"), show_alert=True)
        return

    if bot_obj.bot_type == BotType.BOT:
        token_status = (
            i18n.get("bot-token-valid")
            if bot_obj.token_valid
            else i18n.get("bot-token-invalid")
        )
        text = i18n.get(
            "bot-view",
            name=bot_obj.name or "—",
            username=bot_obj.username or "—",
            bot_id=bot_obj.tg_bot_id or "—",
            token=bot_obj.token or "—",
            token_status=token_status,
            comment=bot_obj.comment or "—",
            extra_info=bot_obj.extra_info or "—",
        )
    else:
        text = i18n.get(
            "project-view",
            name=bot_obj.name or "—",
            link=bot_obj.link or "—",
            comment=bot_obj.comment or "—",
            extra_info=bot_obj.extra_info or "—",
        )

    await call.message.edit_text(
        text=text,
        reply_markup=inline.bot_view(
            callback_data, is_bot=(bot_obj.bot_type == BotType.BOT)
        ),
    )
    await call.answer()


@router.callback_query(BotCallbackData.filter(F.action == "refresh_token"))
async def refresh_token(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    i18n: I18nContext,
    bot_repo: BotRepository,
    bot: Bot,
):
    bot_obj = await bot_repo.get_by_id(callback_data.id)
    if not bot_obj or not bot_obj.token:
        await call.answer(text=i18n.get("bot-not-found"), show_alert=True)
        return

    try:
        check_bot = Bot(token=bot_obj.token)
        await check_bot.get_me()
        await check_bot.session.close()
        await bot_repo.update(bot_obj.id, token_valid=True)
        await call.answer(text=i18n.get("bot-token-refreshed"), show_alert=True)
    except TelegramUnauthorizedError:
        await bot_repo.update(bot_obj.id, token_valid=False)
        await call.answer(text=i18n.get("bot-token-refresh-failed"), show_alert=True)
    except Exception:
        await bot_repo.update(bot_obj.id, token_valid=False)
        await call.answer(text=i18n.get("bot-token-refresh-failed"), show_alert=True)


@router.callback_query(BotCallbackData.filter(F.action == "delete"))
async def bot_delete_ask(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    bot_obj = await bot_repo.get_by_id(callback_data.id)
    if not bot_obj:
        await call.answer(text=i18n.get("bot-not-found"), show_alert=True)
        return
    name = bot_obj.username or bot_obj.name or str(bot_obj.id)
    await call.message.edit_text(
        text=i18n.get("bot-delete-confirm", name=name),
        reply_markup=inline.bot_delete_confirm(callback_data),
    )
    await call.answer()


@router.callback_query(BotCallbackData.filter(F.action == "delete_confirm"))
async def bot_delete_confirm(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    await bot_repo.delete(callback_data.id)
    bots = await bot_repo.get_by_server(callback_data.server_id, page=1)
    count = await bot_repo.count_by_server(callback_data.server_id)
    await call.message.edit_text(
        text=i18n.get("bot-deleted") + "\n\n" + i18n.get("bots-list" if count > 0 else "bots-empty"),
        reply_markup=inline.bots_list(
            bots, count, callback_data.server_id, callback_data.client_id, page=1
        ),
    )
    await call.answer()
