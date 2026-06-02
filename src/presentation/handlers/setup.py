from aiogram import Dispatcher

from src.presentation.handlers import admin, user


def setup_modules(dp: Dispatcher):
    for module in [admin, user]:
        module.reg_packages(dp)
