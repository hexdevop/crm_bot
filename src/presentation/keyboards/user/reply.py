from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram_i18n import I18nContext


def skip_and_cancel(i18n: I18nContext) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=i18n.get("skip"))
    builder.button(text=i18n.get("cancel"))
    return builder.adjust(1).as_markup(
        resize_keyboard=True, input_field_placeholder="«💢 Отмена» чтобы вернутся"
    )


def main_menu(i18n: I18nContext, is_client: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    if is_client:
        builder.button(text=i18n.get("r-user-my-servers"))
        builder.button(text=i18n.get("r-user-my-bots"))
    return builder.adjust(2).as_markup(
        resize_keyboard=True,
        input_field_placeholder=i18n.get("placeholder-user-main-menu"),
    )
