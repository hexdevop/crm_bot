from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject, Command
from sqlalchemy.ext.asyncio import AsyncSession
from tabulate import tabulate

from sqlalchemy import text
import re
from src.infrastructure.cache.manager import cache_manager

router = Router()


@router.message(Command("file_id"))
async def get_file_id(message: types.Message, command: CommandObject):
    if message.reply_to_message and message.reply_to_message.content_type != "text":
        if message.reply_to_message.content_type == "photo":
            return await message.answer(text=message.reply_to_message.photo[-1].file_id)
        await message.answer(
            text=getattr(
                message.reply_to_message, message.reply_to_message.content_type
            ).file_id
        )
    if command.args:
        try:
            try:
                await message.reply_photo(photo=command.args)
            except TelegramBadRequest:
                await message.reply_animation(animation=command.args)
        except Exception as err:
            await message.answer(text=str(err))


@router.message(Command("json"))
async def send_json(
    message: types.Message,
):
    if message.reply_to_message:
        try:
            await message.answer(
                text=f'<pre language="json">{message.reply_to_message.model_dump(exclude_none=True)}</>'
            )
        except TelegramBadRequest:
            pass


@router.message(Command("html"))
async def send_json(
    message: types.Message,
):
    if message.reply_to_message:
        try:
            await message.answer(
                text=message.reply_to_message.html_text, parse_mode=None
            )
        except TelegramBadRequest:
            pass


@router.message(Command("sql"))
async def sql_command(
    message: types.Message,
    command: CommandObject,
    session: AsyncSession,
):
    if not command.args:
        await message.reply(
            "Пожалуйста, укажите SQL-запрос. Пример: /sql SELECT * FROM users;"
        )
        return

    query = command.args
    normalized = query.strip().lower()

    try:
        # For SELECT-like queries, execute and fully materialize results within the session
        if (
            normalized.startswith("select")
            or normalized.startswith("show")
            or normalized.startswith("describe")
            or normalized.startswith("explain")
        ):
            result = await session.execute(text(query))
            # Materialize everything while the session/connection is still open
            headers = list(result.keys())
            rows = result.fetchall()
            data = [tuple(r) for r in rows]
            affected_rows = len(data)

            if data:
                response = tabulate(data, headers=headers, tablefmt="pretty")
            else:
                response = "Результатов нет."
        else:
            # For mutating queries, run and commit explicitly
            result = await session.execute(text(query))
            await session.commit()
            affected_rows = result.rowcount if result.rowcount is not None else 0
            response = "Запрос выполнен успешно."

            # Попытка определить таблицы и сбросить кэш
            tables = re.findall(
                r"(?:from|update|into|table|truncate)\s+([a-zA-Z0-9_]+)",
                normalized,
                re.IGNORECASE,
            )

            cleared_tables = []
            if tables:
                for table in set(tables):
                    await cache_manager.delete_pattern(f"{table}:*")
                    cleared_tables.append(table)

            if cleared_tables:
                response += f"\n\nСброшен кэш для таблиц: {', '.join(cleared_tables)}"
            else:
                # Если таблицы не определены, но запрос мутирующий, можно сбросить весь кэш или ничего не делать
                # В данном случае просто сообщим, что кэш не был сброшен автоматически
                response += (
                    "\n\nНе удалось автоматически определить таблицы для сброса кэша."
                )

        response += f"\n\nЗатронуто записей: {affected_rows}"
        await message.reply(f"```\n{response}\n```", parse_mode="Markdown")

    except Exception as e:
        # Обработка ошибок
        await message.reply(f"Ошибка при выполнении запроса: {e}")
