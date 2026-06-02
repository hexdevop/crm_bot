from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.infrastructure.repo.client import ClientRepository
from src.infrastructure.repo.bot import BotRepository
from src.presentation.keyboards.admin.factory import BotCallbackData
from src.presentation.keyboards.user import inline, reply
from src.presentation.states.user import UserBotSearchState
from src.utils.message import delete_messages

router = Router()


@router.callback_query(BotCallbackData.filter(F.action == "user_bot_search"))
async def start_user_search(
    call: types.CallbackQuery,
    state: FSMContext,
    i18n: I18nContext,
    client_repo: ClientRepository,
):
    client = await client_repo.get_by_telegram_id(call.from_user.id)
    if not client:
        await call.answer(text=i18n.get("user-not-client"), show_alert=True)
        return

    await state.update_data(search_client_id=client.id)
    msg = await call.message.answer(
        text=i18n.get("user-bot-search-prompt"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(UserBotSearchState.query)
    await call.answer()


@router.message(UserBotSearchState.query, F.text)
async def process_user_search(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    data = await state.get_data()
    await delete_messages(message, data)

    query = message.text.strip()
    client_id = data["search_client_id"]

    results = await bot_repo.search_by_client(client_id, query)
    await state.clear()

    if not results:
        await message.answer(
            text=i18n.get("user-bot-search-empty", query=query),
        )
        return

    await message.answer(
        text=i18n.get("user-bot-search-results", query=query, count=len(results)),
        reply_markup=inline.user_bots_search_results(results),
    )


@router.message(L.cancel(), StateFilter(UserBotSearchState))
async def cancel_user_search(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    from src.presentation.keyboards.user.reply import main_menu
    await message.answer(
        text=i18n.get("user-welcome"),
        reply_markup=main_menu(i18n, is_client=True),
    )
