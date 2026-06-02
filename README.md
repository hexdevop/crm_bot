# CRM Bot

> https://github.com/hexdevop/crm_bot

Telegram-бот для управления клиентами, серверами и проектами фриланс-разработчика.

## Функционал

**Для администратора:**
- Управление клиентами (Telegram ID, имя, username, заметки)
- Управление серверами (IP, порт, SSH-доступ, название)
- Управление ботами и проектами на каждом сервере
- SSH-проверка серверов прямо из бота (аптайм, нагрузка, RAM, диск, Docker)
- Редактирование всех полей
- Ежедневная автопроверка токенов ботов в 00:00

**Для клиентов:**
- Просмотр своих серверов (с SSH-статусом)
- Просмотр своих ботов и проектов с указанием сервера
- Поиск ботов по имени, username или токену
- Установка собственного названия для сервера

## Стек

| Компонент | Технология |
|---|---|
| Telegram | aiogram 3.27 + aiogram-i18n 1.5 |
| База данных | MySQL 8.0 (SQLAlchemy 2.0 + aiomysql) |
| Кеш / FSM | Redis 7 |
| SSH | asyncssh |
| Миграции | Alembic |
| Планировщик | APScheduler 3 |
| Логирование | Loguru |

## Быстрый старт

```bash
cp .env.example .env
# Заполнить .env
docker compose up -d --build
```

**Production:**

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

**Локально** (Python 3.11+, MySQL и Redis должны быть запущены):

```bash
pip install -r requirements.txt
alembic upgrade head
python -m src.cmd.bot
```

## Конфигурация (.env)

```env
ENV=dev                            # dev | prod

BOT_TOKEN=123456789:ABCDEF...
ADMIN_IDS=[123456789]              # Telegram ID администраторов
SKIP_UPDATES=false

DB_HOST=localhost
DB_PORT=3306
DB_USER=appuser
DB_PASS=password
DB_ROOT_PASS=rootpassword          # Только для Docker
DB_NAME=bot_db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB_FSM=0
REDIS_DB_CACHE=1
REDIS_DB_JOB=2

USE_WEBHOOK=false
WEBHOOK_URL=https://your-domain.com
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=your_secret_token
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8080
```

> В Docker `DB_HOST` и `REDIS_HOST` перезаписываются автоматически.

## Миграции

```bash
alembic upgrade head

# После изменения моделей:
alembic revision --autogenerate -m "описание"
alembic upgrade head
```

## Docker-команды

```bash
docker compose logs -f crm_bot
docker compose down
docker compose up -d --build crm_bot
docker exec -it crm_db mysql -u appuser -p bot_db
```
