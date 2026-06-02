from aiogram import Dispatcher

from . import default, main, clients


def reg_packages(dp: Dispatcher):
    for package in [default, main, clients]:
        package.reg_routers(dp)
