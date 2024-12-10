# from __future__ import annotations
from __future__ import annotations

import asyncio
import os
from pprint import pprint
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils import executor
import process_photo
from api_key import api
from keyboards import *

bot_token = api
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())


class PhotoState(StatesGroup):
    waiting_for_description_check = State()
    waiting_for_description = State()
    photos = State()
    type_card = State()
    descriptions = State()
    process = State()


class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: int | float = 0.01):
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]
        else:
            return


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Приветствие для пользователя
    await message.answer('Привет! Давай добавим подписи к твоим фотографиям.', reply_markup=start_kb)


@dp.message_handler(text=['Загрузить фото'])
async def photo_download(message: types.Message):
    await message.answer('Пришли мне несколько фотографий (до 10 шт., размер до 100 МБ).')
    await PhotoState.photos.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=PhotoState.photos)
async def get_message(message: types.Message, album: list[types.Message] = None, state=None):
    if not album:
        album = [message]

    media_group = types.MediaGroup()
    for file in album:
        if file.photo:
            file_id = file.photo[-1].file_id
        else:
            continue

        try:
            file_path = f'UserFiles/Photos/{file_id}.jpg'
            if os.path.exists(file_path):
                pass
            else:
                await file.photo[-1].download(file_path)
            media_group.attach(types.InputMedia(media=file_id, type=file.content_type))

        except ValueError:
            return await message.answer("Что-то пошло не так...")

    await message.answer('Следующие фото были успешно загружены...')
    await message.answer_media_group(media_group)

    await state.update_data(photos=media_group)
    await message.answer('Выбери тип карточки:', reply_markup=card_type_kb)
    await PhotoState.type_card.set()


@dp.callback_query_handler(text=['love_is'], state=PhotoState.type_card)
async def set_type_love_is(call, state):
    await state.update_data(type_card='love_is')
    await call.message.answer('Выбран тип карточки: "Love is..."', reply_markup=next_kb)
    await PhotoState.descriptions.set()


@dp.callback_query_handler(text=['friend_is'], state=PhotoState.type_card)
async def set_type_friend_is(call, state):
    await state.update_data(type_card='friend_is')
    await call.message.answer('Выбран тип карточки: "Friend is..."', reply_markup=next_kb)
    await PhotoState.descriptions.set()


@dp.message_handler(text=['Продолжить'], state=PhotoState.descriptions)
async def request_descriptions(message: types.Message, state):
    data = await state.get_data()
    photos = data['photos']

    descriptions = []
    if photos:
        first_photo = photos.media[0]['media']
        photos.media.remove(photos.media[0])
        await state.update_data(photos=photos)
        await PhotoState.descriptions.set()
        await send_photo(message, first_photo)
        # descriptions.append(desc)
    else:
        await message.answer('🚫 Нет фотографий для обработки.')
    await state.update_data(descriptions=descriptions)


async def send_photo(message: types.Message, photo: str):
    await PhotoState.waiting_for_description.set()
    file_path = f'UserFiles/Photos/{photo}.jpg'
    with open(file_path, 'rb') as img:
        await message.answer_photo(img, caption='Напиши подпись для этого фото')

    # Запрашиваем подтверждение для продолжения
    # await message.answer('Хотите продолжить? (да/нет)', reply_markup=types.ReplyKeyboardMarkup(
    #     keyboard=[
    #         [types.KeyboardButton(text='Да')],
    #         [types.KeyboardButton(text='Нет')]
    #     ],
    #     resize_keyboard=True,
    #     one_time_keyboard=True
    # ))

    # Сохраняем текущее состояние
    # data = await state.get_data()
    # current_photos = data.get('photos', [])
    # await state.update_data(current_photos=current_photos)


@dp.message_handler(state=PhotoState.waiting_for_description)
async def process_confirmation(message: types.Message, state):
    data = await state.get_data()
    current_photos = data.get('photos', [])

    if current_photos.media:
        next_photo = current_photos.media[0]['media']
        current_photos.media.remove(current_photos.media[0])
        # next_photo = current_photos.media[0]['media']
        await state.update_data(photos=current_photos)
        await state.update_data(descriptions={next_photo: message.text})
        await send_photo(message, next_photo)

    else:
        await message.answer('🚫 Все фотографии были обработаны.', reply_markup=start_kb)
        data = await state.get_data()
        print(data['descriptions'])
        await state.finish()  # Завершаем состояние


# @dp.message_handler(text=['Обработать'], state=PhotoState.process)
# async def check(message: types.Message, state):
#     try:
#         # Получить список файлов фотографий
#         photo_list = os.listdir('UserFiles/Photos')
#         data = await state.get_data()
#         photo_descriptions = data['descriptions']
#
#         for photo_id, photo_description in photo_descriptions.items():
#
#             with open(photo_id, 'rb') as photo:
#                 await message.answer_photo(photo, caption='📸 Твоя обработанная фотография.')
#
#         # Удалить все файлы фотографий
#         for photo in photo_list:
#             os.remove(f'UserFiles/Photos/{photo}')
#
#         # Сообщение об успешной обработке
#         await message.answer('✅ Все фотографии успешно обработаны!', reply_markup=start_kb)
#
#     except Unauthorized:
#         # Сообщение об ошибке авторизации
#         await message.answer('🚫 У меня нет разрешения на доступ к твоим фото. Попробуй переустановить бота.')
#
#     finally:
#         # Переход в начальное состояние
#         await state.finish()


if __name__ == '__main__':
    os.makedirs('UserFiles/Photos', exist_ok=True)
    album_middleware = AlbumMiddleware()
    dp.middleware.setup(album_middleware)
    executor.start_polling(dp, skip_updates=True)
