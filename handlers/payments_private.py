import asyncio
import os
import time
import uuid

from dotenv import find_dotenv, load_dotenv

from loguru import logger
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from filters.chat_types import ChatTypeFilter, PaymentsTypeFilter
from aiogram.fsm.context import FSMContext

from fsmForProject.FSM_For_project import ForPaySub, ForPayTrial
from handlers.Additional_functionals.request_for_AI import (days_to_secs, append_to_json, read_to_json,
                                                            substitution_to_json, initClient, QuickpayForYouMoney, SubscriptionVerification)
from kbds.reply import get_keyboard, answer_sub_inline

load_dotenv(find_dotenv())
logger.add("error.log", level="ERROR", rotation="100 MB", compression="zip", enqueue=True)

payments_private_router = Router()
payments_private_router.message.filter(ChatTypeFilter(['private']))
idnt_label_for_pay = 0

@payments_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Здравствуйте! Выберите, что вы хотите сделать:', reply_markup=get_keyboard(
                             "Купить подписку","Попробовать бота бесплатно","Уже есть подписка",
                             placeholder="Что вас интересует?",
                             sizes=(2, 2)
                        ))

@payments_private_router.message(F.text == "Купить подписку")
async def one_cmd(message: types.Message, state: FSMContext):
    await state.set_state(ForPaySub.to_buy)
    await message.answer('Тарифные планы:', reply_markup=answer_sub_inline)

@payments_private_router.callback_query(F.data == "submonth", ForPaySub.to_buy)
async def payments_callback_query_month(callback_query: types.CallbackQuery, state: FSMContext):
    loop = asyncio.get_running_loop()
    await callback_query.message.delete()
    global idnt_label_for_pay
    idnt_label_for_pay = uuid.uuid4()
    link_to_pay = await loop.run_in_executor(None, QuickpayForYouMoney, os.getenv('RECEIVER'), idnt_label_for_pay, 249,
                                             'Покупка подписки на месяц')
    await callback_query.message.answer(f'Тариф: Подписка на месяц (249р)\nПерейдите по ссылке и проведите оплату:\n\n{str(link_to_pay)}\n\nЗатем нажмите на кнопку ОПЛАТИЛ для завершения платежа', reply_markup=get_keyboard(
        "Оплатил",
        sizes=(2, 2)
    ))
    await state.update_data(to_buy=30)
    await state.set_state(ForPaySub.successful_payment)


@payments_private_router.callback_query(F.data == "subweek", ForPaySub.to_buy)
async def payments_callback_query_week(callback_query: types.CallbackQuery, state: FSMContext):
    loop = asyncio.get_running_loop()
    await callback_query.message.delete()
    global idnt_label_for_pay
    idnt_label_for_pay = uuid.uuid4()
    link_to_pay = await loop.run_in_executor(None, QuickpayForYouMoney, os.getenv('RECEIVER'), idnt_label_for_pay, 149,
                                             'Покупка подписки на неделю')
    await callback_query.message.answer(
        f'Тариф: Подписка на неделю (149р)\nПерейдите по ссылке и проведите оплату:\n\n{str(link_to_pay)}\n\nЗатем нажмите на кнопку ОПЛАТИЛ для завершения платежа',
        reply_markup=get_keyboard(
        "Оплатил",
        sizes=(2, 2)
    ))

    await state.update_data(to_buy=7)
    await state.set_state(ForPaySub.successful_payment)


@payments_private_router.message(ForPaySub.successful_payment, F.text == "Оплатил")
async def successful_payment_cmd(message: types.Message, state: FSMContext):

    global idnt_label_for_pay
    loop = asyncio.get_running_loop()
    client_youmoney = await loop.run_in_executor(None, initClient, os.getenv('YOOMONEYTOKEN'))
    result = await loop.run_in_executor(None, SubscriptionVerification, client_youmoney, idnt_label_for_pay)

    if result:
        payments_term = await state.get_data()
        days_secs = await days_to_secs(payments_term["to_buy"])
        time_now = int(time.time())
        general_time = days_secs + time_now
        data_for_check = await read_to_json("DATA.json")
        idnt_label_for_pay = 0
        for data_for_user in data_for_check:
            if data_for_user['userId'] == message.from_user.id:
                await substitution_to_json(message.from_user.id,'start',general_time, "DATA.json")
                await substitution_to_json(message.from_user.id, 'main_time', time_now, "DATA.json")
                await substitution_to_json(message.from_user.id, 'in_start_time_sub', time_now, "DATA.json")
                break
        else:
            await append_to_json({"userId":message.from_user.id,
                                  "basic":True,
                                  "trial":False,
                                  "start": general_time,
                                  'main_time':time_now,
                                  'in_start_time_sub':time_now}, "DATA.json")
        await message.answer('Оплата успешна!')
        await state.update_data(successful_payment=True)
        await state.clear()
        await message.answer('Выберите, что хотите сделать?', reply_markup=get_keyboard(
            "Заменить фон", "Добавить текст",
            placeholder="Что вас интересует?",
            sizes=(2, 2)))


@payments_private_router.message(F.text == "Попробовать бота бесплатно")
async def two_cmd(message: types.Message, state: FSMContext):
    await state.set_state(ForPayTrial.decision_confirmation)
    await message.answer('Вы точно хотите опробовать бесплатно?', reply_markup=get_keyboard(
                             "Да","Нет",
                             sizes=(2, 2)
                        ))

@payments_private_router.message(F.text == ("Да" or 'да' or 'lf'), ForPayTrial.decision_confirmation)
async def three_cmd(message: types.Message, state: FSMContext):
    await state.update_data(decision_confirmation = True)
    data_for_check = await read_to_json("DATA.json")
    for data_for_user in data_for_check:
        if data_for_user['userId'] == message.from_user.id:
            if data_for_user['trial'] == False:
                days_secs = await days_to_secs(1)
                time_now = int(time.time())
                general_time = days_secs + time_now
                await substitution_to_json(message.from_user.id, 'trial', True, "DATA.json")
                await substitution_to_json(message.from_user.id, 'start', general_time, "DATA.json")
                await substitution_to_json(message.from_user.id, 'main_time', time_now, "DATA.json")
                await substitution_to_json(message.from_user.id, 'in_start_time_sub', time_now, "DATA.json")
                await message.answer('У вас действует бесплатная подписка')
                await state.clear()
                await message.answer('Выберите, что хотите сделать?', reply_markup=get_keyboard(
                    "Заменить фон", "Добавить текст",
                    placeholder="Что вас интересует?",
                    sizes=(2, 2)))
                break
            else:
                await message.answer('Вы уже использовали бесплатную подписку. Выберете другой способ: ', reply_markup=get_keyboard(
                    "Купить подписку",
                    sizes=(2, 2)))
                break
    else:
        days_secs = await days_to_secs(1)
        time_now = int(time.time())
        general_time = days_secs + time_now
        await append_to_json({"userId": message.from_user.id,
                              "basic": False,
                              "trial": True,
                              "start": general_time,
                              'main_time':time_now,
                              'in_start_time_sub':time_now}, "DATA.json")
        await message.answer('У вас действует бесплатная подписка')
        await state.clear()
        await message.answer('Выберите, что хотите сделать?', reply_markup=get_keyboard(
            "Заменить фон", "Добавить текст",
            placeholder="Что вас интересует?",
            sizes=(2, 2)))


@payments_private_router.message(F.text == ("Нет" or 'нет' or 'ytn'),  ForPayTrial.decision_confirmation)
async def three_cmd(message: types.Message, state: FSMContext):
    await state.update_data(decision_confirmation = True)
    await state.clear()
    await message.answer('Хорошо. Выберете, что хотите сделать: ', reply_markup=get_keyboard(
                             "Купить подписку","Попробовать бота бесплатно","Уже есть подписка",
                             sizes=(2, 2)
                        ))


@payments_private_router.message(F.text == "Уже есть подписка")
async def if_is_sub(message: types.Message):
    verification = PaymentsTypeFilter()
    verification_data = await verification(message)
    if verification_data == True:
        await message.answer('Хорошо, выберите, что хотите сделать?',reply_markup=get_keyboard(
                                     "Заменить фон","Добавить текст",
                                     placeholder="Что вас интересует?",
                                     sizes=(2, 2)))
    else:
        await message.answer('У вас нет активных подписок')
