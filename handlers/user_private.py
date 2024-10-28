import asyncio
import traceback

from loguru import logger
from aiogram import Router, types, F
from aiogram.filters import Command
from filters.chat_types import ChatTypeFilter, PaymentsTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from commands.bot_cmds_list import text_for_instruction
from fsmForProject.FSM_For_project import ForPromt, ForTheme, ForAddText
from handlers.Additional_functionals.request_for_AI import remove_image_background_24AI, create_image_background_24AI, \
    size_of_photo, add_text_to_photo, remove_image_background, create_dir, delete_dir, size_of_photo_for_center, \
    time_sub_day, read_to_json
from kbds.reply import get_keyboard, catalog_list_theme, del_kbd

logger.add("..\error.log",level="ERROR", rotation="100 MB", compression="zip", enqueue=True)

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']), PaymentsTypeFilter())



try:
    @user_private_router.message(Command('work'))
    async def start_cmd(message: types.Message):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, delete_dir, f"createText_{message.from_user.id}")
        await loop.run_in_executor(None, delete_dir, message.from_user.id)
        await message.answer('Здравствуйте! Выберите, что вы хотите сделать:', reply_markup=get_keyboard(
                                 "Заменить фон","Добавить текст",
                                 placeholder="Что вас интересует?",
                                 sizes=(2, 2)
                            ))


    @user_private_router.message(Command('time'))
    async def start_cmd(message: types.Message):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, delete_dir, f"createText_{message.from_user.id}")
        await loop.run_in_executor(None, delete_dir, message.from_user.id)
        data = await read_to_json("DATA.json")
        for i in data:
            if i["userId"] == message.from_user.id:
                time_of_json = i["start"]
                old_time_now = i["main_time"]
                break
        user_sub = await time_sub_day(time_of_json, old_time_now)
        if user_sub == False:
            await message.answer("У вас закончилась подписка. Преобретите новую.")
        else:
            user_sub = "Подписка: " + user_sub
            await message.answer(user_sub, reply_markup=get_keyboard(
                "Заменить фон", "Добавить текст",
                placeholder="Что вас интересует?",
                sizes=(2, 2)
            ))


    @user_private_router.message(Command("instruction"))
    async def instruction_cmd(message: types.Message):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, delete_dir, f"createText_{message.from_user.id}")
        await loop.run_in_executor(None, delete_dir, message.from_user.id)
        await message.answer(text_for_instruction[0], reply_markup=get_keyboard(
            "Заменить фон", "Добавить текст",
            placeholder="Что вас интересует?",
            sizes=(2, 2)
        ))


    @user_private_router.message(F.text == ("Добавить текст" or "добавить текст" or "lj,fdbnm ntrcn" or "добавитьтекст" or "Добавитьтекст"))
    async def one_cmd_for_text(message: types.Message, state: FSMContext):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, delete_dir, f"createText_{message.from_user.id}")
        await loop.run_in_executor(None, create_dir, f"createText_{message.from_user.id}")
        await state.set_state(ForAddText.photo)
        await message.reply('Скиньте фотку, на которую хотите добавить текст:', reply_markup=del_kbd)


    @user_private_router.message(ForAddText.photo, F.photo)
    async def two_cmd_for_text(message: types.Message, state: FSMContext):
        await state.update_data(photo = message.photo[-1].file_id)
        file_of_photo = await state.get_data()
        await message.bot.download(file=file_of_photo["photo"],
                                   destination=f"handlers/photos_for_createText_{message.from_user.id}/photo_for_text_{message.from_user.id}.png")
        await state.update_data(photo=f"photo_for_text_{message.from_user.id}.png")
        await state.set_state(ForAddText.color_of_text)
        await message.reply('Какой цвет текста вы бы хотели?', reply_markup=get_keyboard(
                                 "Чёрный","Белый",
                                 sizes=(2, 2)))

    @user_private_router.message(ForAddText.color_of_text, F.text.in_({"Чёрный", "Белый"}))
    async def three_cmd_for_text(message: types.Message, state: FSMContext):
        await state.update_data(color_of_text=message.text)
        await state.set_state(ForAddText.text_for_photo)
        await message.reply("Напишите текст, который хотите видеть\nЕсли у вас текст в две строки, "
                            "то напишите между строками вот этот знак - '_'", reply_markup=del_kbd)

    @user_private_router.message(ForAddText.text_for_photo, F.text)
    async def four_cmd_for_text(message: types.Message, state: FSMContext):
        loop = asyncio.get_running_loop()
        await state.update_data(text_for_photo=message.text)
        data = await state.get_data()
        await loop.run_in_executor(None, add_text_to_photo, f"photos_for_createText_{message.from_user.id}/{data["photo"]}",
                                data["text_for_photo"],
                                data["color_of_text"])
        await message.reply_photo(FSInputFile(f"handlers/photos_for_createText_{message.from_user.id}/{data["photo"]}"))
        await message.answer("Вот изображение с текстом:", reply_markup=get_keyboard(
            "Заменить фон","Добавить текст",
            placeholder="Что вас интересует?",
            sizes=(2, 1))
                             )
        await state.clear()
        await loop.run_in_executor(None, delete_dir, f"createText_{message.from_user.id}")




    @user_private_router.message(F.text == ("Заменить фон" or "заменить фон" or "pfvtybnm ajy" or "заменитьфон"))
    async def one_cmd(message: types.Message):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, delete_dir, message.from_user.id)
        await message.reply('Вы хотите заменить фон с готовой темой или ввести своё описание изображения?', reply_markup=get_keyboard(
                                 "Выбрать готовую тему","Написать свой промт",
                                 placeholder="Что вас интересует?",
                                 sizes=(2, 2)))




    @user_private_router.message(F.text == 'Написать свой промт')
    async def two_cmd_for_promt(message: types.Message, state: FSMContext):
        loop = asyncio.get_running_loop()
        await state.set_state(ForPromt.photography_for_generation)
        await loop.run_in_executor(None, create_dir, message.from_user.id)
        await message.reply('Загрузите, пожалуйста, фото:', reply_markup=del_kbd)



    @user_private_router.message(ForPromt.photography_for_generation, F.photo)
    async def three_cmd_for_promt(message: types.Message, state: FSMContext):
        await state.update_data(photography_for_generation=message.photo[-1].file_id)
        file_of_photo = await state.get_data()
        await message.bot.download(file=file_of_photo["photography_for_generation"],
                                   destination=f"handlers/photos_for_{message.from_user.id}/"
                                               f"image_for_ai_{message.from_user.id}.png")
        await state.set_state(ForPromt.position_object)
        await message.reply('Где вы хотите расположить объект?', reply_markup=get_keyboard(
            "По центру", "Как на фото",
            placeholder="Сообщение"),
                            sizes=(2, 1))

    @user_private_router.message(ForPromt.position_object, F.text.in_({"По центру", "по центру", "Как на фото", "как на фото"}))
    async def four_cmd_for_promt(message: types.Message, state: FSMContext):
        await state.update_data(position_object=message.text.lower())
        await state.set_state(ForPromt.photo_for_style_generation)
        await message.reply('Пришлите фото желаемого стиля (если не хотите, напишите "Нет"):', reply_markup=del_kbd)

    @user_private_router.message(ForPromt.photo_for_style_generation, F.text == ("Нет" or "нет" or "НЕТ"))
    async def five_cmd_for_promt(message: types.Message, state: FSMContext):
        await state.update_data(photo_for_style_generation = None)
        await state.set_state(ForPromt.promt)
        await message.reply('Опишите желаемый фон:')

    @user_private_router.message(ForPromt.photo_for_style_generation, F.photo)
    async def five_cmd_for_promt(message: types.Message, state: FSMContext):
        await state.update_data(photo_for_style_generation=message.photo[-1].file_id)
        file_of_photo = await state.get_data()
        await message.bot.download(file=file_of_photo["photo_for_style_generation"],
                                   destination=f"handlers/photos_for_{message.from_user.id}/image_for_style_ai_{message.from_user.id}.png")
        await state.update_data(photo_for_style_generation=f"image_for_style_ai_{message.from_user.id}.png")
        await state.set_state(ForPromt.promt)
        await message.reply('Опишите желаемый фон:')

    @user_private_router.message(ForPromt.promt, F.text)
    async def six_cmd_for_promt(message: types.Message, state: FSMContext):
        await state.update_data(promt=message.text)
        await state.set_state(ForPromt.negative_promt)
        await message.reply('Напишите, что вы не хотите видеть в генерации:')

    @user_private_router.message(ForPromt.negative_promt, (F.text & F.text != 'Выбрать готовую тему'))
    async def seven_cmd_for_promt(message: types.Message, state: FSMContext):
        loop = asyncio.get_running_loop()
        await state.update_data(negative_promt=message.text)
        all_data = await state.get_data()
        message_for_delete = await message.answer("Подождите немного, пожалуйста...")
        if all_data["position_object"] == "как на фото":
            await loop.run_in_executor(None, remove_image_background, f"photos_for_{message.from_user.id}/image_for_ai_{message.from_user.id}.png",
                                          f"photos_for_{message.from_user.id}/output_{message.from_user.id}.png")
            width, height, x, y = await loop.run_in_executor(None, size_of_photo, f"photos_for_{message.from_user.id}/output_{message.from_user.id}.png")
        elif all_data["position_object"] == "по центру":
            await remove_image_background_24AI(
                f"photos_for_{message.from_user.id}/image_for_ai_{message.from_user.id}.png",
                f"photos_for_{message.from_user.id}/output_{message.from_user.id}.png")
            width, height, x, y = await loop.run_in_executor(None, size_of_photo_for_center,f"photos_for_{message.from_user.id}/output_{message.from_user.id}.png")
        data = await create_image_background_24AI(name_of_image_file=f"output_{message.from_user.id}.png",
                                                  styleImage=f"{all_data["photo_for_style_generation"]}",
                                                  promt=all_data["promt"],
                                                  negative_promt=all_data["negative_promt"],
                                                  themeId=None,
                                                  width= width,
                                                  height=height,
                                                  message_id_from_user=message.from_user.id,
                                                  x=x,
                                                  y=y
                                                  )
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_for_delete.message_id)
        if data == "Success":
            await message.reply_photo(FSInputFile(f'handlers/photos_for_{message.from_user.id}/generation_output_{message.from_user.id}.png'))
            await state.set_state(ForPromt.repeat_output)
            await message.answer("Вот и сгенерированное изображение, хотите сгенерировать заново с теми же данными?", reply_markup=get_keyboard(
                                 "Да", "Нет",
                                 placeholder="Что вас интересует?",
                                 sizes=(2, 1))
            )

        else:
            await message.reply(f'Не получилось из-за статуса {data}, немного подождите и попробуйте ещё раз')

    @user_private_router.message(ForPromt.repeat_output, F.text)
    async def eight_cmd_for_promt(message: types.Message, state: FSMContext):
        loop = asyncio.get_running_loop()
        await state.update_data(repeat_output=message.text)
        all_data = await state.get_data()
        if str(all_data["repeat_output"]).lower() == "да":
            message_for_delete = await message.answer("Подождите немного, пожалуйста...")
            if all_data["position_object"] == "как на фото":
                width, height, x, y = await loop.run_in_executor(None, size_of_photo,f"photos_for_{message.from_user.id}/output_{message.from_user.id}.png")
            elif all_data["position_object"] == "по центру":
                width, height, x, y = await loop.run_in_executor(None, size_of_photo_for_center, f"photos_for_{message.from_user.id}/output_{message.from_user.id}.png")
            data = await create_image_background_24AI(name_of_image_file=f"output_{message.from_user.id}.png",
                                                      styleImage=f"{all_data["photo_for_style_generation"]}",
                                                      promt=all_data["promt"],
                                                      negative_promt=all_data["negative_promt"],
                                                      themeId=None,
                                                      width=width,
                                                      height=height,
                                                      message_id_from_user=message.from_user.id,
                                                      x=x,
                                                      y=y
                                                      )
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message_for_delete.message_id)
            if data == "Success":
                await message.reply_photo(FSInputFile(f'handlers/photos_for_{message.from_user.id}/generation_output_{message.from_user.id}.png'))
                await state.set_state(ForPromt.repeat_output)
                await message.answer("Вот и сгенерированное изображение, хотите сгенерировать заново с теми же данными?", reply_markup=get_keyboard(
                                 "Да", "Нет",
                                 placeholder="Что вас интересует?",
                                 sizes=(2, 1)))
            else:
                await message.reply(f'Не получилось из-за статуса {data}, немного подождите и попробуйте ещё раз')

        elif str(all_data["repeat_output"]).lower() == "нет":
            await state.clear()
            await loop.run_in_executor(None, delete_dir, message.from_user.id)
            await message.answer("Выберите, что вы хотите сделать:",
                                 reply_markup=get_keyboard(
                                     "Выбрать готовую тему","Написать свой промт", "Добавить текст",
                                     placeholder="Что вас интересует?",
                                     sizes=(2, 1)))




    @user_private_router.message(F.text == 'Выбрать готовую тему')
    async def two_cmd(message: types.Message, state: FSMContext):
        loop = asyncio.get_running_loop()
        await state.set_state(ForTheme.photography_for_generation)
        await loop.run_in_executor(None, create_dir, message.from_user.id)
        await message.reply('Загрузите, пожалуйста, фото:', reply_markup=del_kbd)

    @user_private_router.message(ForTheme.photography_for_generation, F.photo)
    async def three_cmd(message: types.Message, state: FSMContext):
        await state.update_data(photography_for_generation=message.photo[-1].file_id)
        file_of_photo = await state.get_data()
        await message.bot.download(file=file_of_photo["photography_for_generation"],
                                   destination=f"handlers/photos_for_{message.from_user.id}/"
                                               f"image_for_ai_{message.from_user.id}.png")
        await state.set_state(ForTheme.position_object)
        await message.reply('Где вы хотите расположить объект?', reply_markup=get_keyboard(
                                    "По центру","Как на фото",
                                 placeholder="Сообщение"),
                                sizes=(2,1))

    @user_private_router.message(ForTheme.position_object, F.text.in_({"По центру", "по центру", "Как на фото", "как на фото"}))
    async def four_cmd(message: types.Message, state: FSMContext):
        await state.update_data(position_object=message.text.lower())
        await state.set_state(ForTheme.getting_for_themeId)
        await message.answer('Выберите тему:', reply_markup=catalog_list_theme)


    @user_private_router.callback_query(ForTheme.getting_for_themeId)
    async def callback_query_five(callback_query: types.CallbackQuery, state: FSMContext):
        loop = asyncio.get_running_loop()
        await state.update_data(getting_for_themeId=callback_query.data)
        name_of_theme = await state.get_data()
        message_for_delete = await callback_query.message.answer("Подождите немного, пожалуйста...")
        if name_of_theme["position_object"] == "как на фото":
            await loop.run_in_executor(None, remove_image_background, f"photos_for_{callback_query.from_user.id}/image_for_ai_{callback_query.from_user.id}.png", f"photos_for_{callback_query.from_user.id}/output_{callback_query.from_user.id}.png")
            width, height, x, y = await loop.run_in_executor(None, size_of_photo, f"photos_for_{callback_query.from_user.id}/output_{callback_query.from_user.id}.png")
        elif name_of_theme["position_object"] == "по центру":
            await remove_image_background_24AI(f"photos_for_{callback_query.from_user.id}/image_for_ai_{callback_query.from_user.id}.png", f"photos_for_{callback_query.from_user.id}/output_{callback_query.from_user.id}.png")
            width, height, x, y = await loop.run_in_executor(None, size_of_photo_for_center, f"photos_for_{callback_query.from_user.id}/output_{callback_query.from_user.id}.png")
        data = await create_image_background_24AI(name_of_image_file=f"output_{callback_query.from_user.id}.png",
                                                  styleImage="None",
                                                  promt=None,
                                                  negative_promt=None,
                                                  themeId=name_of_theme["getting_for_themeId"],
                                                  width=width,
                                                  height=height,
                                                  message_id_from_user=callback_query.from_user.id,
                                                  x=x,
                                                  y=y
                                                  )

        await callback_query.message.bot.delete_message(chat_id=callback_query.message.chat.id, message_id=message_for_delete.message_id)
        if data == "Success":
            await callback_query.message.reply_photo(FSInputFile(f'handlers/photos_for_{callback_query.from_user.id}/generation_output_{callback_query.from_user.id}.png'))
            await state.set_state(ForTheme.repeat_output)
            await callback_query.message.answer("Вот и сгенерированное изображение, хотите сгенерировать заново с теми же данными?",
                                 reply_markup=get_keyboard(
                                     "Да", "Нет",
                                     placeholder="Что вас интересует?",
                                     sizes=(2, 1))
                                 )

        else:
            await callback_query.message.reply(f'Не получилось из-за статуса {data}, немного подождите и попробуйте ещё раз')

    @user_private_router.message(ForTheme.repeat_output, F.text)
    async def six_cmd(message: types.Message, state: FSMContext):
        loop = asyncio.get_running_loop()
        await state.update_data(repeat_output=message.text)
        name_of_theme = await state.get_data()
        if str(name_of_theme["repeat_output"]).lower() == "да":
            message_for_delete = await message.answer("Подождите немного, пожалуйста...")
            if name_of_theme["position_object"] == "как на фото":
                width, height, x, y = await loop.run_in_executor(None, size_of_photo, f"photos_for_{message.from_user.id}/output_{message.from_user.id}.png")
            elif name_of_theme["position_object"] == "по центру":
                width, height, x, y = await loop.run_in_executor(None, size_of_photo_for_center, f"photos_for_{message.from_user.id}/output_{message.from_user.id}.png")
            data = await create_image_background_24AI(name_of_image_file=f"output_{message.from_user.id}.png",
                                                  styleImage="None",
                                                  promt=None,
                                                  negative_promt=None,
                                                  themeId=name_of_theme["getting_for_themeId"],
                                                  width=width,
                                                  height=height,
                                                  message_id_from_user=message.from_user.id,
                                                  x=x,
                                                  y=y
                                                  )
            await message.bot.delete_message(chat_id=message.chat.id,
                                             message_id=message_for_delete.message_id)
            if data == "Success":
                await message.reply_photo(FSInputFile(f'handlers/photos_for_{message.from_user.id}/generation_output_{message.from_user.id}.png'))
                await state.set_state(ForTheme.repeat_output)
                await message.answer("Вот и сгенерированное изображение, хотите сгенерировать заново с теми же данными?",
                                     reply_markup=get_keyboard(
                                         "Да", "Нет",
                                         placeholder="Что вас интересует?",
                                         sizes=(2, 1)))

            else:
                await message.reply(f'Не получилось из-за статуса {data}, немного подождите и попробуйте ещё раз')

        elif str(name_of_theme["repeat_output"]).lower() == "нет":
            await state.clear()
            await loop.run_in_executor(None, delete_dir, message.from_user.id)
            await message.answer("Выберите, что вы хотите сделать:",
                                 reply_markup=get_keyboard(
                                     "Выбрать готовую тему","Написать свой промт", "Добавить текст",
                                     placeholder="Что вас интересует?",
                                     sizes=(2, 1)))
except Exception:
    e = traceback.format_exc()
    logger.error(e)
