import asyncio
from dataclasses import dataclass

SSH_CACHE_TTL = 300  # 5 minutes
SSH_CACHE_PREFIX = "ssh:"


@dataclass
class ServerInfo:
    is_tcp_open: bool = False
    is_ssh_auth: bool = False
    uptime: str = ""
    load_1: float = 0.0
    load_5: float = 0.0
    load_15: float = 0.0
    ram_used_mb: int = 0
    ram_total_mb: int = 0
    disk_used: str = ""
    disk_total: str = ""
    disk_percent: str = ""
    docker_count: int = -1
    error: str = ""


async def _check_tcp(host: str, port: int, timeout: float = 5.0) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return True
    except Exception:
        return False


def _progress_bar(percent: int, width: int = 10) -> str:
    filled = int(width * percent / 100)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def _parse_info(info: ServerInfo, lines: list[str]) -> None:
    try:
        secs = float(lines[0].split()[0])
        d, rem = divmod(int(secs), 86400)
        h, m = divmod(rem, 3600)
        m //= 60
        info.uptime = f"{d}д {h}ч {m}м" if d else (f"{h}ч {m}м" if h else f"{m}м")
    except (IndexError, ValueError):
        pass

    try:
        parts = lines[1].split()
        info.load_1, info.load_5, info.load_15 = (
            float(parts[0]), float(parts[1]), float(parts[2])
        )
    except (IndexError, ValueError):
        pass

    try:
        parts = lines[2].split()
        info.ram_total_mb, info.ram_used_mb = int(parts[1]), int(parts[2])
    except (IndexError, ValueError):
        pass

    try:
        parts = lines[3].split()
        info.disk_total, info.disk_used, info.disk_percent = (
            parts[1], parts[2], parts[4]
        )
    except (IndexError, ValueError):
        pass

    try:
        info.docker_count = int(lines[4].strip())
    except (IndexError, ValueError):
        info.docker_count = -1


async def check_server(ip: str, port: int, user: str, password: str | None) -> ServerInfo:
    info = ServerInfo()
    info.is_tcp_open = await _check_tcp(ip, port)

    if not info.is_tcp_open:
        info.error = f"Порт {port} закрыт"
        return info

    if not password:
        info.error = "Пароль не задан — SSH не попробован"
        return info

    try:
        import asyncssh  # noqa: PLC0415

        async with asyncssh.connect(
            ip,
            port=port,
            username=user,
            password=password,
            known_hosts=None,
            connect_timeout=10.0,
        ) as conn:
            info.is_ssh_auth = True
            result = await conn.run(
                "cat /proc/uptime && cat /proc/loadavg && "
                "free -m | grep '^Mem' && "
                "df -h / | tail -1 && "
                "docker ps -q 2>/dev/null | wc -l",
                timeout=15,
            )
            _parse_info(info, result.stdout.strip().split("\n"))

    except Exception as e:
        name = type(e).__name__
        if "PermissionDenied" in name or "AuthenticationError" in name:
            info.error = "Неверные учётные данные SSH"
        elif "ConnectionLost" in name or "ConnectionRefused" in name:
            info.error = "Соединение отклонено"
        elif "TimeoutError" in name:
            info.error = "Тайм-аут SSH"
        else:
            info.error = str(e)[:120]

    return info


def format_result(ip: str, port: int, info: ServerInfo) -> str:
    if not info.is_tcp_open:
        return (
            f"🔴 <b>Сервер недоступен</b>\n"
            f"❌ {info.error}"
        )

    if not info.is_ssh_auth:
        return (
            f"🟡 <b>TCP открыт / SSH недоступен</b>\n"
            f"ℹ️ {info.error}"
        )

    ram_pct = int(info.ram_used_mb / info.ram_total_mb * 100) if info.ram_total_mb else 0
    ram_bar = _progress_bar(ram_pct)

    parts = [
        "🟢 <b>SSH доступен</b>",
        f"⏱ Аптайм: <b>{info.uptime}</b>",
        f"📊 Нагрузка (1/5/15): <b>{info.load_1:.2f}</b> / {info.load_5:.2f} / {info.load_15:.2f}",
        f"💾 RAM: <b>{info.ram_used_mb} MB</b> / {info.ram_total_mb} MB  {ram_bar} {ram_pct}%",
        f"💿 Диск /: <b>{info.disk_used}</b> / {info.disk_total} ({info.disk_percent})",
    ]
    if info.docker_count >= 0:
        parts.append(f"🐳 Docker: <b>{info.docker_count}</b> контейнеров")

    return "\n".join(parts)


async def get_or_check_ssh(
    ip: str,
    port: int,
    user: str,
    password: str | None,
    server_id: int,
    cache,
    force: bool = False,
) -> str:
    cache_key = f"{SSH_CACHE_PREFIX}{server_id}"

    if not force:
        cached = await cache.get(cache_key)
        if cached:
            return cached

    info = await check_server(ip, port, user, password)
    result = format_result(ip, port, info)
    await cache.set(cache_key, result, ttl=SSH_CACHE_TTL)
    return result


async def invalidate_ssh_cache(server_id: int, cache) -> None:
    await cache.delete(f"{SSH_CACHE_PREFIX}{server_id}")
