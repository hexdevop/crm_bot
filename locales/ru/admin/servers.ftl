servers-list =
    <b>🖥 Серверы клиента</b>

    Выберите сервер или добавьте новый

servers-empty = Серверов пока нет. Нажмите кнопку ниже, чтобы добавить.

server-view =
    <b>🖥 { $name }</b>

    🌐 IP: <code>{ $ip }</code>
    🔌 Порт: <code>{ $port }</code>
    👤 Пользователь: <code>{ $user }</code>
    🔑 Пароль: <code>{ $password }</code>
    📝 Доп. инфо: { $extra_info }

    🤖 Ботов: <b>{ $bots_count }</b>

ssh-checking-inline = Проверяю SSH...

server-add-ip =
    Введите <b>IP-адрес</b> сервера:
    (например: <code>192.168.1.1</code>)

server-add-port =
    Введите <b>порт</b> SSH:
    (по умолчанию: <code>22</code>, или нажмите «Пропустить»)

server-add-user =
    Введите <b>пользователя</b> сервера:
    (по умолчанию: <code>root</code>, или нажмите «Пропустить»)

server-add-password =
    Введите <b>пароль</b> сервера:
    Или нажмите «Пропустить»

server-add-extra =
    Введите <b>дополнительную информацию</b>:
    (хостинг, регион, заметки — или нажмите «Пропустить»)

server-add-name =
    Введите <b>название</b> сервера для себя:
    (например: <code>VPS Production</code> — или нажмите «Пропустить»)

server-edit-name =
    Введите <b>новое название</b> сервера:
    Нажмите «Пропустить» чтобы очистить

server-edit-ip = Введите <b>новый IP-адрес</b>:

server-edit-port = Введите <b>новый порт</b> SSH:

server-edit-user = Введите <b>нового пользователя</b> сервера:

server-edit-pass =
    Введите <b>новый пароль</b> сервера:
    Или нажмите «Пропустить» чтобы очистить

server-edit-extra =
    Введите <b>новую доп. информацию</b>:
    Или нажмите «Пропустить» чтобы очистить

ssh-checking = ⏳ Проверяю подключение к <code>{ $ip }:{ $port }</code>...

server-added = ✅ Сервер <b>{ $ip }</b> добавлен!

server-not-found = ❌ Сервер не найден

server-deleted = ✅ Сервер удалён

server-delete-confirm =
    ❓ Удалить сервер <b>{ $ip }</b>?

    ⚠️ Это также удалит всех его ботов!
