from typing import Dict, Any, List
from aiogram_i18n.cores import BaseCore
from fluent.runtime import FluentLocalization
from src.infrastructure.localization.loader import get_fluent_localization


class CustomFluentCore(BaseCore):
    def __init__(self, default_locale: str = "en", locales: List[str] = None):
        super().__init__(path="locales", default_locale=default_locale)
        self.locales_map: Dict[str, FluentLocalization] = get_fluent_localization(
            locales
        )

    def get(self, message: str, locale: str | None = None, /, **kwargs: Any) -> str:
        if locale is None:
            locale = self.default_locale

        localization = self.locales_map.get(locale)
        if not localization:
            localization = self.locales_map.get(self.default_locale)
            if not localization:
                return message

        return localization.format_value(message, kwargs)

    @property
    def available_locales(self) -> List[str]:
        return list(self.locales_map.keys())

    def find_locales(self) -> Dict[str, Any]:
        return self.locales_map
