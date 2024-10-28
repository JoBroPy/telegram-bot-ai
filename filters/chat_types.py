from aiogram.filters import Filter
from aiogram import types
from handlers.Additional_functionals.request_for_AI import read_to_json


# Определение фильтра для проверки на нужные нам типы чата (Eng. Defining a filter to check for the chat types we need)
class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


# Определение фильтра для проверки на "оплатил ли пользователь подписку или нет"
# (Eng. Defining a filter to check for “whether the user has paid for the subscription or not”)
class PaymentsTypeFilter(Filter):
    def __init__(self):
        pass

    async def __call__(self, message:types.Message) -> bool:
        all_usersId: list = await read_to_json("DATA.json")
        for i in all_usersId:
            if i["userId"] == message.from_user.id and i["start"] != 0:
                return True
        return False
