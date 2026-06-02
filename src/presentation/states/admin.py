from aiogram.fsm.state import StatesGroup, State


class RefState(StatesGroup):
    name = State()
    price = State()


class ExportState(StatesGroup):
    menu = State()


class VariableState(StatesGroup):
    value = State()


class ClientState(StatesGroup):
    telegram_id = State()
    name = State()
    username = State()


class ServerState(StatesGroup):
    ip = State()
    port = State()
    user = State()
    password = State()
    extra_info = State()
    name = State()


class BotAddState(StatesGroup):
    bot_type = State()
    token = State()
    name = State()
    link = State()
    extra_info = State()
    comment = State()


class EditClientState(StatesGroup):
    value = State()


class EditServerState(StatesGroup):
    value = State()


class EditBotState(StatesGroup):
    value = State()


class BotSearchState(StatesGroup):
    query = State()
