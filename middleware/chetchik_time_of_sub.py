import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from handlers.Additional_functionals.request_for_AI import time_sub_day, substitution_to_json, read_to_json


# Класс для логики проверки состояния пользователя в базе данных(json-файле).
# Проверка на каждом telegram апдейте. (Eng. Class for the logic of checking user status in the database(json file).
# Check on every telegram update)
class CounterMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.data_for_json = []
        self.time_of_json = 0
        self.choise = None
        self.id_for_remove = None
        self.main_time_of_json = 0
        self.in_start_time_sub = 0
        self.global_in_start_time_sub = int(time.time())


    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Проверка через недавно добавленную конструкции match ... case
        # Проверка происходит смотря какой апдейт подаётся, всего бот взаимодейтсвует с 3 апдейтами
        # Далее он проверяет есть ли пользователь в бд или нет и задаёт нужные данные, если есть
        # Eng.
        # Check via the recently added match construct ... case
        # The check happens depending on which update is submitted, the bot interacts with 3 updates in total.
        # Then it checks whether the user is in the database or not and sets the necessary data if he is.
        match event.event_type:
            case "message":
                self.data_for_json = await read_to_json("DATA.json")
                if len(self.data_for_json) != 0:
                    for i in self.data_for_json:
                        if i["userId"] == event.message.from_user.id and i['start'] != 0:
                            self.id_for_remove = event.message.from_user.id
                            self.time_of_json = i["start"]
                            self.main_time_of_json = i['main_time']
                            if self.global_in_start_time_sub > i['in_start_time_sub']:
                                self.in_start_time_sub = self.global_in_start_time_sub
                            else:
                                self.in_start_time_sub = i['in_start_time_sub']
                            self.choise = False
                            break
                        else:
                            self.choise = True
                else:
                    self.choise = True
            case "edited_message":
                self.data_for_json = await read_to_json("DATA.json")
                if len(self.data_for_json) != 0:
                    for i in self.data_for_json:
                        if i["userId"] == event.edited_message.from_user.id and i['start'] != 0:
                            self.id_for_remove = event.edited_message.from_user.id
                            self.time_of_json = i["start"]
                            self.main_time_of_json = i['main_time']
                            if self.global_in_start_time_sub > i['in_start_time_sub']:
                                self.in_start_time_sub = self.global_in_start_time_sub
                            else:
                                self.in_start_time_sub = i['in_start_time_sub']
                            self.choise = False
                            break
                        else:
                            self.choise = True
                else:
                    self.choise = True
            case "callback_query":
                self.data_for_json = await read_to_json("DATA.json")
                if len(self.data_for_json) != 0:
                    for i in self.data_for_json:
                        if i["userId"] == event.callback_query.from_user.id and i['start'] != 0:
                            self.id_for_remove = event.callback_query.from_user.id
                            self.time_of_json = i["start"]
                            self.main_time_of_json = i['main_time']
                            if self.global_in_start_time_sub > i['in_start_time_sub']:
                                self.in_start_time_sub = self.global_in_start_time_sub
                            else:
                                self.in_start_time_sub = i['in_start_time_sub']
                            self.choise = False
                            break
                        else:
                            self.choise = True
                else:
                    self.choise = True

        # Считает время и прогоняет его через условие, если никакое условие не срабатывает,
        # то просто задаёт новое время, которое осталось до окончания подписки
        # Eng.
        # Counts the time and runs it through a condition, if no condition is triggered,
        # it simply sets a new time left until the subscription expires

        ftl = await time_sub_day(self.time_of_json, self.main_time_of_json, type_for='middleware')
        if ftl == False and self.choise == False:
            await substitution_to_json(self.id_for_remove,'start', 0, "DATA.json")
            self.time_of_json = 0
            return await handler(event, data)
        elif ftl == False and self.choise == True:
            return await handler(event, data)
        await substitution_to_json(self.id_for_remove, 'start', self.time_of_json-(int(time.time())-self.in_start_time_sub), "DATA.json")
        await substitution_to_json(self.id_for_remove, 'in_start_time_sub', int(time.time()), "DATA.json")
        return await handler(event, data)
