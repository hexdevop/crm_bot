from aiogram import Router, types, F, Bot
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.domain.bot import TgBot, BotType
from src.infrastructure.repo.bot import BotRepository
from src.presentation.keyboards.admin import inline, reply
from src.presentation.keyboards.admin.factory import BotCallbackData
from src.presentation.states.admin import BotAddState
from src.utils.message import delete_messages

router = Router()


@router.message(L.cancel(), StateFilter(BotAddState))
async def cancel_bot_add(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    await message.answer(
        text=i18n.get("admin-menu"), reply_markup=reply.main_admin(i18n)
    )


@router.callback_query(BotCallbackData.filter(F.action == "add"))
async def start_add_bot(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    state: FSMContext,
    i18n: I18nContext,
):
    await state.update_data(
        server_id=callback_data.server_id, client_id=callback_data.client_id
    )
    await call.message.edit_text(
        text=i18n.get("bot-add-type"),
        reply_markup=inline.bot_type_select(
            callback_data.server_id, callback_data.client_id
        ),
    )
    await call.answer()


@router.callback_query(BotCallbackData.filter(F.action == "add_bot"))
async def add_tg_bot_start(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    state: FSMContext,
    i18n: I18nContext,
):
    await call.message.delete()
    await state.update_data(
        server_id=callback_data.server_id,
        client_id=callback_data.client_id,
        bot_type=BotType.BOT,
    )
    msg = await call.message.answer(
        text=i18n.get("bot-add-token"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(BotAddState.token)
    await call.answer()


@router.message(BotAddState.token, F.text)
async def get_bot_token(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
):
    data = await state.get_data()
    await delete_messages(message, data)

    token = message.text.strip()
    try:
        check_bot = Bot(token=token)
        bot_info = await check_bot.get_me()
        await check_bot.session.close()
    except Exception:
        msg = await message.answer(
            text=i18n.get("bot-invalid-token"),
            reply_markup=reply.skip_and_cancel(i18n),
        )
        await state.update_data(message_id=msg.message_id)
        return

    await state.update_data(
        token=token,
        tg_bot_id=bot_info.id,
        name=bot_info.first_name,
        username=bot_info.username,
    )
    msg = await message.answer(
        text=i18n.get("bot-add-extra"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(BotAddState.extra_info)


@router.callback_query(BotCallbackData.filter(F.action == "add_project"))
async def add_project_start(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    state: FSMContext,
    i18n: I18nContext,
):
    await call.message.delete()
    await state.update_data(
        server_id=callback_data.server_id,
        client_id=callback_data.client_id,
        bot_type=BotType.PROJECT,
    )
    msg = await call.message.answer(
        text=i18n.get("bot-add-name"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(BotAddState.name)
    await call.answer()


@router.message(BotAddState.name, F.text)
async def get_project_name(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
):
    data = await state.get_data()
    await delete_messages(message, data)
    await state.update_data(name=message.text.strip())
    msg = await message.answer(
        text=i18n.get("bot-add-link"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(BotAddState.link)


@router.message(BotAddState.link, F.text)
async def get_project_link(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
):
    data = await state.get_data()
    await delete_messages(message, data)
    skip_text = i18n.get("skip")
    link = None if message.text == skip_text else message.text.strip()
    await state.update_data(link=link)
    msg = await message.answer(
        text=i18n.get("bot-add-extra"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(BotAddState.extra_info)


@router.message(BotAddState.extra_info, F.text)
async def get_extra_info(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
):
    data = await state.get_data()
    await delete_messages(message, data)
    skip_text = i18n.get("skip")
    extra = None if message.text == skip_text else message.text.strip()
    await state.update_data(extra_info=extra)
    msg = await message.answer(
        text=i18n.get("bot-add-comment"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(BotAddState.comment)


@router.message(BotAddState.comment, F.text)
async def get_comment_and_save(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    data = await state.get_data()
    await delete_messages(message, data)
    skip_text = i18n.get("skip")
    comment = None if message.text == skip_text else message.text.strip()

    bot_type = data.get("bot_type", BotType.BOT)

    server_id = data["server_id"]
    client_id = data.get("client_id", 0)

    if bot_type == BotType.BOT:
        tg_bot = await bot_repo.add(
            TgBot(
                server_id=server_id,
                bot_type=BotType.BOT,
                tg_bot_id=data["tg_bot_id"],
                name=data["name"],
                username=data["username"],
                token=data["token"],
                token_valid=True,
                extra_info=data.get("extra_info"),
                comment=comment,
            )
        )
        added_text = i18n.get("bot-added", username=tg_bot.username or tg_bot.name)
    else:
        project = await bot_repo.add(
            TgBot(
                server_id=server_id,
                bot_type=BotType.PROJECT,
                name=data["name"],
                link=data.get("link"),
                extra_info=data.get("extra_info"),
                comment=comment,
            )
        )
        added_text = i18n.get("project-added", name=project.name)

    await state.clear()

    bots = await bot_repo.get_by_server(server_id, page=1)
    count = await bot_repo.count_by_server(server_id)
    await message.answer(
        text=added_text + "\n\n" + i18n.get("bots-list" if count > 0 else "bots-empty"),
        reply_markup=inline.bots_list(bots, count, server_id, client_id, page=1),
    )
