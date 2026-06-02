from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram_i18n import I18nContext
from src.application.services.user_service import UserService
from src.core.config import settings
from src.infrastructure.repo.client import ClientRepository
from src.presentation.keyboards.admin import reply as admin_reply
from src.presentation.keyboards.user import reply as user_reply

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: types.Message,
    user_service: UserService,
    i18n: I18nContext,
    client_repo: ClientRepository,
    ref: str = None,
):
    user = await user_service.get_or_create_user(
        from_user=message.from_user,
        ref=ref,
    )

    if user.id in settings.ADMIN_IDS:
        await message.answer(
            text=i18n.get("admin-menu"),
            reply_markup=admin_reply.main_admin(i18n),
        )
        return

    client = await client_repo.get_by_telegram_id(message.from_user.id)
    if not client:
        await message.answer(text=i18n.get("user-not-client"))
        return

    await message.answer(
        text=i18n.get("user-welcome"),
        reply_markup=user_reply.main_menu(i18n, is_client=True),
    )
