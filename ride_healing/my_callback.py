from aiogram.filters.callback_data import CallbackData
class MyCallback(CallbackData, prefix="my"):
    name: str
    id: int