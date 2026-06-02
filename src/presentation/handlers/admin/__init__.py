from aiogram import Dispatcher, Router

from . import main, clients, servers, bots, commands
from src.presentation.filters.admin import IsAdminFilter
from src.presentation.middlewares.locale import AdminLocaleMiddleware


def reg_packages(dp: Dispatcher):
    admin_root = Router()
    admin_root.message.middleware(AdminLocaleMiddleware())

    for package in [main, clients, servers, bots]:
        package.reg_routers(admin_root)

    commands.router.message.filter(IsAdminFilter())
    admin_root.include_router(commands.router)

    dp.include_router(admin_root)
