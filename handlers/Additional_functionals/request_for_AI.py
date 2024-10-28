import os
import aiohttp
import traceback
from loguru import logger
from dotenv import find_dotenv, load_dotenv
import base64
from PIL import Image, ImageDraw, ImageFont
from rembg import remove, new_session
from cryptography.fernet import Fernet
import asyncj
import datetime
import ast
import aiofiles
from yoomoney import Quickpay, Client

load_dotenv(find_dotenv())

headers = {'Authorization': f'Token {os.getenv('TOKEN')}'}
logger.add("..\..\error.log",level="ERROR", rotation="100 MB", compression="zip", enqueue=True)
fernet = Fernet(bytes(str(os.getenv('KEY')), encoding="utf-8"))

def initClient(token): # Инициализирует клиент из yoomoney (Eng. Initializes the client from yoomoney)
    try:
        client = Client(token)
        return client
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

def QuickpayForYouMoney(receiver, idnt, summa, targets): # Возвращает ссылку на оплату (Eng. Returns a link to the payment)
    try:
        quickpay = Quickpay(
            receiver=receiver,
            quickpay_form="shop",
            targets=targets,
            paymentType="SB",
            sum=summa,
            label=idnt
        )
        return quickpay.base_url
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

def SubscriptionVerification(client, label): # Проверка на оплату через Client YooMoney (Eng. Checking for payment via Client YooMoney)
    try:
        history = client.operation_history(label=label)
        for operation in history.operations:
            if operation.status == 'success':
                return True
            return False
    except Exception:
        e = traceback.format_exc()
        logger.error(e)


async def get_themes_list_24AI():

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            response = await session.get('https://core.24ai.tech/api/v1/themes')
            content = await response.json()
        return content
    except Exception:
        e = traceback.format_exc()
        logger.error(e)


def size_of_photo(path_to_photo): # Возвращает размеры загружаемого фото (Eng. Returns the dimensions of the uploaded photo)
    try:
        image = Image.open(f"handlers/{path_to_photo}")
        width, height = image.size
        return width, height, 1, 1
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

def size_of_photo_for_center(path_to_photo): # Возвращает специальные, зависящие от размера фотки, координаты для центрирования объекта
    # (Eng. Returns special coordinates, depending on the size of the photo, for centering the object)
    try:
        image = Image.open(f"handlers/{path_to_photo}")
        width, height = image.size
        if width <= 350 and height <= 350:
            width = 450
            height = 450
            y = 90
            x = 100
            return width, height, x, y
        elif width <= 450 and height <= 450:
            width = 750
            height = 750
            y = 272
            x = 228
            return width, height, x, y
        elif width <= 500 and height <= 550:
            width = 1250
            height = 1250
            y = 425
            x = 417
            return width,height,x,y
        elif width <= 500 and height > 550:
            height = 1250+(height - 500)
            width = 1250
            y = 425
            x = 417
            return width, height, x, y
        elif width > 500 and height <= 550:
            width = 1250+(width - 550)
            height = 1250
            y = 425
            x = 417
            return width, height, x, y
        elif width > 500 and height > 550:
            width = 1250+(width - 550)
            height = 1250 + (height - 500)
            y = 425
            x = 417
            return width, height, x, y
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

def add_text_to_photo(path_to_photo, text_to_photo : str, color_of_text):

    try:
        img = Image.open(f'handlers/{path_to_photo}')
        draw = ImageDraw.Draw(img)
        width, height = img.size
        data = {
            "Чёрный": "black",
            "Белый": "white"
        }
        if "_" in text_to_photo:
            text_to_photo = str(text_to_photo).replace("_", "\n")

        region = ((width/2)-385, ((height/2)/4)-325, (width/2)+385, ((height/2)/4)+325)

        draw.rectangle(region, width=0)

        font_size = 300
        font = ImageFont.truetype("/root/.fonts/FiraSans-Medium.ttf", font_size)

        x = int((region[2] - region[0]) / 2) + region[0]
        y = int((region[3] - region[1]) / 2) + region[1]
        while font_size > 1:
            bbox = draw.textbbox((x, y), text_to_photo, font=font, anchor="mm", align="center")
            if bbox[0] > region[0] and bbox[1] > region[1] and bbox[2] < region[2] and bbox[3] < region[3]:
                break
            font_size -= 1
            font = font.font_variant(size=font_size)

        draw.text((x, y), text_to_photo, font=font, fill=data[color_of_text], anchor="mm", align="center")
        img.save(f'handlers/{path_to_photo}')
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

async def create_image_background_24AI(name_of_image_file: str,
                                       promt: str,
                                       message_id_from_user,
                                       negative_promt:str,
                                       styleImage=None,
                                       width: int = 1250,
                                       height: int = 1250,
                                       themeId = "0712422b-8f04-4003-aa67-baf67fa5b540",
                                       styleColor = None,
                                       angle: int = 0,
                                       scaleX: int = 1,
                                       scaleY: int = 1,
                                       x: int = 1,
                                       y: int = 1):

    try:

        async with aiofiles.open(f'handlers/photos_for_{message_id_from_user}/{name_of_image_file}', 'rb') as img:
            value = await img.read()
            image = base64.b64encode(value).decode('utf-8')

        if styleImage != "None":
            async with aiofiles.open(f'handlers/photos_for_{message_id_from_user}/{styleImage}', 'rb') as img:
                value = await img.read()
                image_for_generation = base64.b64encode(value).decode('utf-8')
        else:
            image_for_generation = None

        async with aiohttp.ClientSession(headers=headers) as session:
            data = {
              "image": image,
              "styleImage": image_for_generation,
              "description": promt,
              "negative": negative_promt,
              "size": {
                "width": width,
                "height": height
              },
              "themeId": themeId,
              "styleColor": styleColor,
              "transform": {
                "angle": angle,
                "scaleX": scaleX,
                "scaleY": scaleY,
                "x": x,
                "y": y
              }
            }

            response = await session.post(url="https://core.24ai.tech/api/v1/create-background", json=data)
            img_generation = await response.json()

            if response.status == 200:
                decoded_img_data = base64.b64decode((img_generation["data"]["image"]))
                async with aiofiles.open(f'handlers/photos_for_{message_id_from_user}/generation_output_{message_id_from_user}.png', 'wb') as img_file:
                    await img_file.write(decoded_img_data)
                return "Success"

            else:
                return "Error:", response.status
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

def remove_image_background(input_path, output_path):
    try:
        input = Image.open(f'handlers/{input_path}')
        output = remove(input, session=new_session("u2net"),
                        post_process_mask=True)
        output.save(f'handlers/{output_path}')
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

async def remove_image_background_24AI(input_path, output_path):

    try:

        async with aiofiles.open(f'handlers/{input_path}', 'rb') as img:
            value = await img.read()
            image = base64.b64encode(value).decode('utf-8')

        async with aiohttp.ClientSession(headers=headers) as session:
            data = {
                "image": image,
                "trimTransparency": False
            }
            response = await session.post(url="https://core.24ai.tech/api/v1/remove-background", data=data)
            img_without_background = await response.json()

        if response.status == 200:
            decoded_img_data = base64.b64decode((img_without_background["data"]["image"]))
            async with aiofiles.open(f'handlers/{output_path}', 'wb') as img_file:
                await img_file.write(decoded_img_data)
            return "Success"

        else:
            return "Error:", response.status
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

def create_dir(user_id_for_dir):
    try:
        if not os.path.isdir(f"handlers/photos_for_{user_id_for_dir}"):
            os.mkdir(f"handlers/photos_for_{user_id_for_dir}")
    except Exception:
        e = traceback.format_exc()
        logger.error(e)


def delete_dir(user_id_for_dir):
    try:
        if os.path.isdir(f"handlers/photos_for_{user_id_for_dir}"):
            for i in os.listdir(f"handlers/photos_for_{user_id_for_dir}"):
                os.remove(f"handlers/photos_for_{user_id_for_dir}/{i}")
            os.rmdir(f"handlers/photos_for_{user_id_for_dir}")
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

async def append_to_json(dataes, path):
    try:
        dataes = bytes(str(dataes), encoding="utf-8")
        encrypted = fernet.encrypt(dataes).decode("utf-8")
        asyncjson = asyncj.AsyncJson(path)
        data = await asyncjson.read()
        data["dataUsers"].append(encrypted)
        await asyncjson.write(data)
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

async def substitution_to_json(user_id, this, new_elem, path):
    try:
        asyncjson = asyncj.AsyncJson(path)
        data = await asyncjson.read()
        for i in data["dataUsers"]:
            ind = data["dataUsers"].index(i)
            decrypted_in_dict = ast.literal_eval(fernet.decrypt(i).decode("utf-8"))
            if decrypted_in_dict["userId"] == user_id:
                decrypted_in_dict[this] = new_elem
                encrypted = fernet.encrypt(bytes(str(decrypted_in_dict), encoding="utf-8")).decode("utf-8")
                data["dataUsers"][ind] = encrypted
                break
        await asyncjson.write(data)
    except Exception:
        e = traceback.format_exc()
        logger.error(e)


async def read_to_json(path):
    try:
        data_of_spis = []
        asyncjson = asyncj.AsyncJson(path)
        data = await asyncjson.read()
        for i in data["dataUsers"]:
            decrypted = fernet.decrypt(i).decode("utf-8")
            decrypted_in_dict = ast.literal_eval(decrypted)
            data_of_spis.append(decrypted_in_dict)
        return data_of_spis
    except Exception:
        e = traceback.format_exc()
        logger.error(e)

async def days_to_secs(days):
    return (days * 24 * 60**2)

async def time_sub_day(get_time, const_start_time, type_for = 'handler'):
    try:
        if int(get_time) <= int(const_start_time):
            return False
        else:
            if type_for == 'handler':
                dt = str(datetime.timedelta(seconds=(int(get_time) - int(const_start_time))))
                dt = dt.replace("days", "Дней")
                dt = dt.replace("day", "День")
                return dt
            elif type_for == "middleware":
                return (int(get_time) - int(const_start_time))
    except Exception:
        e = traceback.format_exc()
        logger.error(e)
