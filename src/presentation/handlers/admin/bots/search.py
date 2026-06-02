from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L

from src.infrastructure.repo.bot import BotRepository
from src.presentation.keyboards.admin import inline, reply
from src.presentation.keyboards.admin.factory import BotCallbackData
from src.presentation.states.admin import BotSearchState
from src.utils.message import delete_messages

router = Router()


@router.callback_query(BotCallbackData.filter(F.action == "search"))
async def start_search(
    call: types.CallbackQuery,
    callback_data: BotCallbackData,
    state: FSMContext,
    i18n: I18nContext,
):
    await state.update_data(
        search_server_id=callback_data.server_id,
        search_client_id=callback_data.client_id,
    )
    msg = await call.message.answer(
        text=i18n.get("bot-search-prompt"),
        reply_markup=reply.skip_and_cancel(i18n),
    )
    await state.update_data(message_id=msg.message_id)
    await state.set_state(BotSearchState.query)
    await call.answer()


@router.message(BotSearchState.query, F.text)
async def process_search(
    message: types.Message,
    state: FSMContext,
    i18n: I18nContext,
    bot_repo: BotRepository,
):
    data = await state.get_data()
    await delete_messages(message, data)

    query = message.text.strip()
    server_id = data.get("search_server_id", 0)
    client_id = data.get("search_client_id", 0)

    results = await bot_repo.search(query)
    await state.clear()

    if not results:
        await message.answer(
            text=i18n.get("bot-search-empty", query=query),
            reply_markup=inline.bots_list(
                [], 0, server_id=server_id, client_id=client_id
            ),
        )
        return

    await message.answer(
        text=i18n.get("bot-search-results", query=query, count=len(results)),
        reply_markup=inline.bots_search_results(results, server_id, client_id),
    )


@router.message(L.cancel(), StateFilter(BotSearchState))
async def cancel_search(
    message: types.Message, state: FSMContext, i18n: I18nContext
):
    await state.clear()
    await message.answer(
        text=i18n.get("admin-menu"), reply_markup=reply.main_admin(i18n)
    )
