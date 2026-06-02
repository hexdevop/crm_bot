from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import ChatMemberUpdated
from src.application.services.user_service import UserService
from src.domain.user import UserStatus

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, user_service: UserService):
    await user_service.set_user_status(event.from_user.id, UserStatus.BLOCKED)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated, user_service: UserService):
    await user_service.set_user_status(event.from_user.id, UserStatus.ACTIVE)
