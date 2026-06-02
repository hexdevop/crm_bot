from aiogram.filters.callback_data import CallbackData


class LangCallbackData(CallbackData, prefix="lang"):
    action: str
    locale: str = ""


SUPPORTED_LOCALES: dict[str, str] = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}
