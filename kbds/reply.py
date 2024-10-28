from aiogram.types import KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from handlers.Additional_functionals.request_for_AI import get_themes_list_24AI
import asyncio

del_kbd = ReplyKeyboardRemove()

# Функция по созданию reply-клавиатуры (Eng. Function for creating reply-keyboard)
def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (2,),
):
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона"
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:

            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)


data_of_themeIds = asyncio.run(get_themes_list_24AI()) # Сбор данных в словарь с сайта (Eng. Collecting data to the dictionary from the website )

# Создание инлайн-клавиатуры для выбора тем для генерации картинки (Eng. Creating an inline keyboard for selecting themes for image generation)
catalog_list_theme = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Удиви меня", callback_data=data_of_themeIds["data"][0]["id"]),
    InlineKeyboardButton(text="Студия", callback_data=data_of_themeIds["data"][1]["id"]),
    InlineKeyboardButton(text="На улице", callback_data=data_of_themeIds["data"][2]["id"])],

    [InlineKeyboardButton(text="Шёлк", callback_data=data_of_themeIds["data"][3]["id"]),
    InlineKeyboardButton(text="Кафе", callback_data=data_of_themeIds["data"][4]["id"]),
    InlineKeyboardButton(text="На столе", callback_data=data_of_themeIds["data"][5]["id"]),
     ],

    [InlineKeyboardButton(text="Кухня", callback_data=data_of_themeIds["data"][6]["id"]),
    InlineKeyboardButton(text="Цветы", callback_data=data_of_themeIds["data"][7]["id"]),
    InlineKeyboardButton(text="Природа", callback_data=data_of_themeIds["data"][8]["id"]),
     ],

    [InlineKeyboardButton(text="Пляж", callback_data=data_of_themeIds["data"][9]["id"]),
    InlineKeyboardButton(text="Ванная", callback_data=data_of_themeIds["data"][10]["id"]),
    InlineKeyboardButton(text="В интерьере", callback_data=data_of_themeIds["data"][11]["id"]),
     ],

    [InlineKeyboardButton(text="Краски", callback_data=data_of_themeIds["data"][12]["id"]),
    InlineKeyboardButton(text="Фрукты", callback_data=data_of_themeIds["data"][13]["id"]),
    InlineKeyboardButton(text="Вода", callback_data=data_of_themeIds["data"][14]["id"]),
     ],

    [InlineKeyboardButton(text="Галька", callback_data=data_of_themeIds["data"][15]["id"]),
    InlineKeyboardButton(text="Снег", callback_data=data_of_themeIds["data"][16]["id"]),
    InlineKeyboardButton(text="Дубай", callback_data=data_of_themeIds["data"][17]["id"]),
     ]
])

# Создание инлайн-клавиатуры для выбора опций подписки (Eng. Creating an inline keyboard for selecting subscription options)
answer_sub_inline = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="30 дней (месяц)\n 249р", callback_data="submonth"),
        InlineKeyboardButton(text="7 дней (неделя)\n 149р", callback_data="subweek")
    ]
])