from aiogram.filters.callback_data import CallbackData


class RefCallbackData(CallbackData, prefix="r"):
    action: str
    page: int
    type: int = 1
    id: int = 0


class ExportCallbackData(CallbackData, prefix="e"):
    action: str
    category: str = "0"
    value: str = "0"


class VariableCallbackData(CallbackData, prefix="v"):
    action: str
    key: str = "0"
    id: int = 0


class ClientCallbackData(CallbackData, prefix="cl"):
    action: str
    page: int = 1
    id: int = 0


class ServerCallbackData(CallbackData, prefix="sv"):
    action: str
    page: int = 1
    id: int = 0
    client_id: int = 0


class BotCallbackData(CallbackData, prefix="bt"):
    action: str
    page: int = 1
    id: int = 0
    server_id: int = 0
    client_id: int = 0
