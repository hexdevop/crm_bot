from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext, L
from src.presentation.keyboards.admin import reply

router = Router()


@router.message(Command("admin"))
@router.message(L.r.admin.back.to.admin.menu())
async def cmd_admin(message: types.Message, state: FSMContext, i18n: I18nContext):
    await state.clear()
    await message.answer(text=i18n.get("admin-menu"), reply_markup=reply.main_admin(i18n))
