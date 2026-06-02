from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram_i18n import I18nContext
from src.infrastructure.repo.user import UserRepository
from src.presentation.keyboards.user import inline
from src.presentation.keyboards.user.factory import LangCallbackData

router = Router()


@router.message(Command("lang"))
async def cmd_lang(message: types.Message, i18n: I18nContext):
    await message.answer(
        text=i18n.get("lang-choose"),
        reply_markup=inline.lang_select(i18n),
    )


@router.callback_query(LangCallbackData.filter(F.action == "set"))
async def set_language_handler(
    call: types.CallbackQuery,
    callback_data: LangCallbackData,
    i18n: I18nContext,
    user_repo: UserRepository,
):
    locale = callback_data.locale
    if locale not in i18n.core.available_locales:
        await call.answer()
        return

    await user_repo.set_language(call.from_user.id, locale)
    i18n.locale = locale
    await call.message.edit_text(text=i18n.get("lang-changed"))
    await call.answer()
