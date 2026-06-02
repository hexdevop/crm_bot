from math import ceil
from typing import Tuple, Union

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext


def calc_length(count: int, width: int, height: int) -> int:
    return ceil(count / (width * height))


def generate_sizes(sizes: list, object_list: list, width: int, height: int):
    for i in range(height):
        size = len(object_list[i * width : (i + 1) * width])
        if size > 0:
            sizes.append(size)
    return sizes


def with_pagination(
    builder: InlineKeyboardBuilder,
    data: CallbackData,
    length: int,
    page: int,
    sizes: list,
    as_markup: bool = True,
    length_text: str = "{page} из {length}",
    page_data_name: str | None = None,
) -> Union[InlineKeyboardMarkup, Tuple[InlineKeyboardBuilder, list]]:
    buttons_count = 0
    if page > 1:
        data.action = "page"
        setattr(data, page_data_name or "page", page - 1)
        builder.button(text="⏪", callback_data=data.pack())
        buttons_count += 1
    if length > 1:
        data.action = "length"
        builder.button(
            text=length_text.format(page=page, length=length), callback_data=data.pack()
        )
        buttons_count += 1
    if page < length:
        data.action = "page"
        setattr(data, page_data_name or "page", page + 1)
        builder.button(text="⏩", callback_data=data.pack())
        buttons_count += 1
    data.action = "page"
    second_row_buttons_count = 0
    if page - 9 > 1:
        setattr(data, page_data_name or "page", page - 10)
        builder.button(text="⏮ 10", callback_data=data.pack())
        second_row_buttons_count += 1
    if page + 9 < length:
        setattr(data, page_data_name or "page", page + 10)
        builder.button(text="10 ⏭", callback_data=data.pack())
        second_row_buttons_count += 1
    if buttons_count > 0:
        sizes.append(buttons_count)
    if second_row_buttons_count > 0:
        sizes.append(second_row_buttons_count)
    if as_markup:
        return builder.adjust(*sizes).as_markup()
    else:
        return builder, sizes


def confirm(
    data: CallbackData,
    i18n: I18nContext,
    confirm_value: str = "confirm",
    cancel_value: str = "cancel",
):
    builder = InlineKeyboardBuilder()
    data.action = confirm_value
    builder.button(text=i18n.get("confirm"), callback_data=data.pack())
    data.action = cancel_value
    builder.button(text=i18n.get("cancel"), callback_data=data.pack())
    return builder.adjust(1).as_markup()


def back(data: CallbackData, i18n: I18nContext, value: str):
    builder = InlineKeyboardBuilder()
    data.action = value
    builder.button(text=i18n.get("back"), callback_data=data.pack())
    return builder.as_markup()


def cancel(data: Union[str, CallbackData], i18n: I18nContext, value: str = None):
    builder = InlineKeyboardBuilder()
    if type(data) is str:
        callback_data = data
    else:
        data.action = value or "cancel"
        callback_data = data.pack()
    builder.button(text=i18n.get("cancel"), callback_data=callback_data)
    return builder.as_markup()
