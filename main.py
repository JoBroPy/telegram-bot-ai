import os
import asyncio
import traceback
from loguru import logger

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy

from dotenv import find_dotenv, load_dotenv

from handlers.payments_private import payments_private_router
from handlers.user_private import user_private_router
from commands.bot_cmds_list import private


from middleware.chetchik_time_of_sub import CounterMiddleware

load_dotenv(find_dotenv())

ALLOWED_UPDATES = ["message", 'edited_message', "callback_query"]


logger.add("error.log",level="ERROR", rotation="100 MB", compression="zip", enqueue=True)

bot = Bot(token=os.getenv('TOKEN_BOT'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)
dp.update.outer_middleware(CounterMiddleware())
dp.include_routers(user_private_router, payments_private_router)


async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
        await bot.set_my_description("SnapBack AI - ваш персональный помощник по созданию инфографики!\nГенерируйте множество изображений "
                                     "вашего продукта с различными фонами всего за один клик.\nЧтобы "
                                     "начать работу, нажмите кнопку  start в меню.\n По команде instruction будет доступна инструкция по пользованию бота")
        await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

if __name__ == '__main__':
    asyncio.run(main())
