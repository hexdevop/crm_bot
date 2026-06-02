from aiogram.fsm.state import StatesGroup, State


class UserBotSearchState(StatesGroup):
    query = State()


class UserServerRenameState(StatesGroup):
    value = State()
