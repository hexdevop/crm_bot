from datetime import datetime, timezone
from aiogram import Bot
from aiogram.exceptions import TelegramUnauthorizedError
from loguru import logger

from src.infrastructure.db.main import session_maker
from src.infrastructure.cache.manager import cache_manager
from src.domain.bot import TgBot
from src.domain.server import Server
from src.infrastructure.repo.bot import BotRepository


async def check_all_bot_tokens(bot: Bot, admin_ids: list[int]):
    logger.info("Запуск проверки токенов ботов...")
    async with session_maker() as session:
        bot_repo = BotRepository(session, TgBot, cache_manager)
        all_bots = await bot_repo.get_all_with_token()

        invalid: list[TgBot] = []
        for tg_bot in all_bots:
            try:
                check = Bot(token=tg_bot.token)
                await check.get_me()
                await check.session.close()
                if not tg_bot.token_valid:
                    await bot_repo.update(
                        tg_bot.id,
                        token_valid=True,
                        last_checked=datetime.now(timezone.utc),
                    )
            except (TelegramUnauthorizedError, Exception):
                try:
                    await check.session.close()
                except Exception:
                    pass
                if tg_bot.token_valid:
                    await bot_repo.update(
                        tg_bot.id,
                        token_valid=False,
                        last_checked=datetime.now(timezone.utc),
                    )
                invalid.append(tg_bot)

        await session.commit()

    if not invalid:
        logger.info("Все токены ботов актуальны")
        return

    logger.warning(f"Найдено {len(invalid)} ботов с недействительными токенами")

    # Группируем по клиентам
    client_map: dict[int, dict] = {}
    for b in invalid:
        if not b.server:
            continue
        client = b.server.client
        if not client:
            continue
        cid = client.id
        if cid not in client_map:
            client_map[cid] = {"telegram_id": client.telegram_id, "bots": []}
        client_map[cid]["bots"].append(b)

    # Сообщение для администратора
    admin_text = "⚠️ <b>Боты с недействительными токенами:</b>\n\n"
    for cid, info in client_map.items():
        admin_text += f"👤 TG ID: <code>{info['telegram_id']}</code>\n"
        for b in info["bots"]:
            name = f"@{b.username}" if b.username else (b.name or str(b.tg_bot_id))
            admin_text += f"  • {name}\n"
        admin_text += "\n"

    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception as e:
            logger.error(f"Ошибка отправки отчёта администратору {admin_id}: {e}")

    # Уведомляем каждого клиента
    for cid, info in client_map.items():
        lines = []
        for b in info["bots"]:
            name = f"@{b.username}" if b.username else (b.name or str(b.tg_bot_id))
            lines.append(f"• {name}")

        client_text = (
            "⚠️ <b>Обнаружены боты с недействительными токенами:</b>\n\n"
            + "\n".join(lines)
            + "\n\nПожалуйста, обновите токены или сообщите @hexdevop."
        )
        try:
            await bot.send_message(info["telegram_id"], client_text)
        except Exception as e:
            logger.error(
                f"Ошибка отправки уведомления клиенту {info['telegram_id']}: {e}"
            )
