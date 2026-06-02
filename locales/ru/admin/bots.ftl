bots-list =
    <b>🤖 Боты и проекты</b>

    Выберите или добавьте нового

bots-empty = Ботов и проектов пока нет.

bot-view =
    <b>🤖 Телеграм бот</b>

    📛 Имя: <b>{ $name }</b>
    👤 Username: @{ $username }
    🆔 Bot ID: <code>{ $bot_id }</code>
    🔑 Токен: <code>{ $token }</code>
    { $token_status }
    📝 Комментарий: { $comment }
    ℹ️ Доп. инфо: { $extra_info }

project-view =
    <b>📦 Проект</b>

    📛 Имя: <b>{ $name }</b>
    🔗 Ссылка: { $link }
    📝 Комментарий: { $comment }
    ℹ️ Доп. инфо: { $extra_info }

bot-token-valid = ✅ Токен: активен
bot-token-invalid = ⚠️ Токен: НЕДЕЙСТВИТЕЛЕН

bot-add-type = Что хотите добавить?

bot-add-token =
    Отправьте <b>токен</b> бота:
    (например: <code>1234567890:ABCdef...</code>)

bot-add-name =
    Введите <b>название</b> проекта:

bot-edit-name = Введите <b>новое название</b>:

bot-add-link =
    Введите <b>ссылку</b> на проект:
    (или нажмите «Пропустить»)

bot-add-extra =
    Введите <b>дополнительную информацию</b>:
    (или нажмите «Пропустить»)

bot-add-comment =
    Введите <b>комментарий</b>:
    (или нажмите «Пропустить»)

bot-search-prompt =
    🔍 Введите <b>@username</b>, имя или часть токена для поиска:

bot-search-empty = 🔍 Ничего не найдено по запросу: <b>{ $query }</b>

bot-search-results = 🔍 Найдено <b>{ $count }</b> по запросу: <b>{ $query }</b>

bot-added = ✅ Бот <b>@{ $username }</b> добавлен!

project-added = ✅ Проект <b>{ $name }</b> добавлен!

bot-invalid-token = ❌ Недействительный токен. Проверьте правильность и попробуйте снова.

bot-not-found = ❌ Бот не найден

bot-deleted = ✅ Удалено

bot-delete-confirm = ❓ Удалить <b>{ $name }</b>?

bot-token-refreshed = ✅ Токен актуален

bot-token-refresh-failed = ❌ Токен недействителен. Обновите токен.

token-check-report =
    ⚠️ <b>Обнаружены боты с недействительными токенами:</b>

{ $list }
    Пожалуйста, обновите токены или удалите ботов из списка.

token-check-ok = ✅ Все токены актуальны
