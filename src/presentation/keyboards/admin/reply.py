from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram_i18n import I18nContext


def main_admin(i18n: I18nContext) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=i18n.get("r-admin-clients"))
    return builder.adjust(1).as_markup(
        resize_keyboard=True, input_field_placeholder="Админ панель 🏚"
    )


def skip_and_cancel(i18n: I18nContext) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=i18n.get("skip"))
    builder.button(text=i18n.get("cancel"))
    return builder.adjust(1).as_markup(
        resize_keyboard=True, input_field_placeholder="«💢 Отмена» чтобы вернутся"
    )
