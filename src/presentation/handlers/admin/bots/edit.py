from aiogram import Router, types, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.domain.bot import BotType
from src.infrastructure.repo.bot import BotRepository
from src.presentation.keyboards.admin import inline, reply
from src.presentation.keyboards.admin.factory import BotCallbackData
from src.presentation.states.admin import EditBotState
from src.utils.message import delete_messages

router = Router()

_EDIT_PROMPTS = {
    "edit_token": "bot-add-token",
    "edit_name": "bot-edit-name",
    "edit_link": "bot-add-link",
    "edit_extra": "bot-add-extra",
    "edit_comment": "bot-add-comment",
}

_EDIT_FIELDS = {
    "edit_name": "name",
    "edit_link": "link",
    "edit_extra": "extra_info",
    "edit_comment": "comment",
}


@router.callback_query(BotCallbackData.filter(F.action.in_(_EDIT_PROMPTS.keys())))
async def start_edit_bot(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    state: FSMContext,
    i18n: I18nContext,
):
    action = callback_data.action
    await state.update_data(
        edit_id=callback_data.id,
        edit_action=action,
        edit_server_id=callback_data.server_id,
        edit_client_id=callback_data.client_id,
    )
    msg = await call.message.answer(
        text=i18n.get(_EDIT_PROMPTS[action]),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(EditBotState.value)
    await call.answer()


@router.message(EditBotState.value, F.text)
async def process_bot_edit(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    data = await state.get_data()
    await delete_messages(message, data)

    action = data["edit_action"]
    entity_id = data["edit_id"]
    server_id = data.get("edit_server_id", 0)
    client_id = data.get("edit_client_id", 0)
    skip_text = i18n.get("skip")

    if action == "edit_token":
        token = message.text.strip()
        try:
            check = Bot(token=token)
            bot_info = await check.get_me()
            await check.session.close()
        except Exception:
            msg = await message.answer(
                text=i18n.get("bot-invalid-token"),
                reply_markup=reply.skip_and_cancel(i18n),
            )
            await state.update_data(message_id=msg.message_id)
            return
        await bot_repo.update(
            entity_id,
            token=token,
            tg_bot_id=bot_info.id,
            name=bot_info.first_name,
            username=bot_info.username,
            token_valid=True,
        )
    else:
        field = _EDIT_FIELDS[action]
        value = None if message.text == skip_text else message.text.strip() or None
        await bot_repo.update(entity_id, **{field: value})

    await state.clear()

    bot_obj = await bot_repo.get_by_id(entity_id)
    cb = BotCallbackData(action="view", id=entity_id, server_id=server_id, client_id=client_id)

    if bot_obj.bot_type == BotType.BOT:
        token_status = (
            i18n.get("bot-token-valid") if bot_obj.token_valid else i18n.get("bot-token-invalid")
        )
        text = i18n.get("field-updated") + "\n\n" + i18n.get(
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
        text = i18n.get("field-updated") + "\n\n" + i18n.get(
            "project-view",
            name=bot_obj.name or "—",
            link=bot_obj.link or "—",
            comment=bot_obj.comment or "—",
            extra_info=bot_obj.extra_info or "—",
        )

    await message.answer(
        text=text,
        reply_markup=inline.bot_view(cb, is_bot=(bot_obj.bot_type == BotType.BOT)),
    )


@router.message(L.cancel(), StateFilter(EditBotState))
async def cancel_edit_bot(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    await message.answer(
        text=i18n.get("admin-menu"), reply_markup=reply.main_admin(i18n)
    )
