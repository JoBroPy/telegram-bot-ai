from aiogram.fsm.state import StatesGroup, State

# Классы для FSM-состояний в handlers (Eng. Classes for FSM states in handlers)

class ForPromt(StatesGroup):
    photography_for_generation = State()
    position_object = State()
    photo_for_style_generation = State()
    promt = State()
    negative_promt = State()
    repeat_output = State()


class ForTheme(StatesGroup):
    photography_for_generation = State()
    position_object = State()
    getting_for_themeId = State()
    repeat_output = State()

class ForAddText(StatesGroup):
    photo = State()
    color_of_text = State()
    text_for_photo = State()

class ForPaySub(StatesGroup):
    to_buy = State()
    successful_payment = State()


class ForPayTrial(StatesGroup):
    decision_confirmation = State()




