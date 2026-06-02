from pathlib import Path
from typing import Dict
from fluent.runtime import FluentLocalization, FluentResourceLoader
from loguru import logger


def get_fluent_localization(
    languages: list | None = None,
) -> Dict[str, FluentLocalization]:
    """
    Загружает FTL файлы для выбранного языка
    :param languages: список кодов языков, по умолчанию ['ru']
    :return: Объект FluentLocalization с загруженными FTL файлами для выбранного языка
    """
    if not languages:
        languages = ["ru"]

    # Проверка директории "locales".
    # Предполагается, что этот файл находится в src/infrastructure/localization/loader.py
    # а локали находятся в корне проекта (например locales)
    # Поэтому нужно подняться на 3 уровня вверх: localization -> infrastructure -> src -> корень
    root_dir = Path(__file__).parent.parent.parent.parent
    locales_dir = root_dir / "locales"

    if not locales_dir.exists():
        err = f'"locales" directory does not exist at {locales_dir}'
        raise FileNotFoundError(err)
    if not locales_dir.is_dir():
        err = f'"{locales_dir}" is not a directory'
        raise NotADirectoryError(err)

    locales_dir = locales_dir.absolute()
    localizations = {}
    for language in languages:
        locale_dir = locales_dir / language
        if not locale_dir.exists() or not locale_dir.is_dir():
            logger.warning(f'Locale directory "{language}" not found, skipping')
            continue

        # Рекурсивный поиск всех .ftl файлов в директории и её поддиректориях
        locale_files = [str(file.absolute()) for file in locale_dir.rglob("*.ftl")]

        if not locale_files:
            logger.warning(f'No .ftl files found for "{language}" locale, skipping')
            continue

        # Loader ожидает шаблон пути или корень
        l10n_loader = FluentResourceLoader(str(locales_dir / "{locale}"))
        localizations[language] = FluentLocalization(
            [language], locale_files, l10n_loader
        )
    return localizations
