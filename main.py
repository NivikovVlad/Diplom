import os
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.utils.exceptions import Unauthorized
import pil
import process_photo
from api_key import api
from keyboards import *


bot_token = api
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())


class PhotoState(StatesGroup):
    photos = State()
    descriptions = State()
    process = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Приветствие для пользователя
    await message.answer('Привет! Давай добавим подписи к твоим фотографиям.', reply_markup=start_kb)


@dp.message_handler(text=['Загрузить фото'])
async def photo_download(message: types.Message):
    await message.answer('Пришли мне несколько фотографий (до 10 шт., размер до 100 МБ).')
    await PhotoState.photos.set()


@dp.message_handler(content_types=['photo'], state=PhotoState.photos)
async def get_photo(message: types.Message, state):
    # Получение информации о загруженном фото
    file_info = await bot.get_file(message.photo[-1].file_id)
    file_path = f'UserFiles/Photos/{file_info.file_unique_id}.jpg'

    if os.path.exists('UserFiles/Photos/' + file_info.file_unique_id + '.jpg'):
        pass
    else:
        await message.photo[-1].download('UserFiles/Photos/' + file_info.file_unique_id + '.jpg')


    print(file_path)
    await state.update_data(photos=file_path)
    # await message.photo[-1].download(file_path)
    await message.answer('Напиши подпись к следующей фотографии:')
    await PhotoState.descriptions.set()


@dp.message_handler(state=PhotoState.descriptions)
async def request_caption(message: types.Message, state):
    # Получить подпись из сообщения
    photo_description = str(message.text.strip())
    data = await state.get_data()
    current_photo_id = data['photos']
    # Получить ID текущей фотографии

    await state.update_data(descriptions={str(current_photo_id): photo_description})
    await message.answer('Все готово, продолжаем?', reply_markup=next_kb)
    await PhotoState.process.set()


@dp.message_handler(text=['Обработать'], state=PhotoState.process)
async def check(message: types.Message, state):
    try:
        # Получить список файлов фотографий
        photo_list = os.listdir('UserFiles/Photos')
        data = await state.get_data()
        photo_descriptions = data['descriptions']

        # Обработка каждой фотографии
        for photo_id, photo_description in photo_descriptions.items():
            # Удалить метаданные из фотографии
            process_photo.remove_metadata(str(photo_id))
            # Добавить подпись
            process_photo.add_caption(str(photo_id), photo_description)

            # Отправить обработанную фотографию пользователю
            with open(photo_id, 'rb') as photo:
                await message.answer_photo(photo, caption='📸 Твоя обработанная фотография.')


        # Удалить все файлы фотографий
        for photo in photo_list:
            os.remove(f'UserFiles/Photos/{photo}')

        # Сообщение об успешной обработке
        await message.answer('✅ Все фотографии успешно обработаны!', reply_markup=start_kb)

    except Unauthorized:
        # Сообщение об ошибке авторизации
        await message.answer('🚫 У меня нет разрешения на доступ к твоим фото. Попробуй переустановить бота.')

    finally:
        # Переход в начальное состояние
        await state.finish()




# class PhotoState(StatesGroup):
#     photos = State()
#     description = State()
#     process = State()
#
#
# @dp.message_handler(commands=['start'])
# async def start_command(message: types.Message):
#     # Приветствие для пользователя
#     await message.answer('Привет! Давайте добавим подписи к вашим фотографиям.', reply_markup=start_kb)
#
#
# @dp.message_handler(text=['Загрузить фото'])
# async def photo_download(message: types.Message):
#     await message.answer('Пришлите несколько фотографий (максимум 10, размером до 100 МБ).')
#     await PhotoState.photos.set()
#
#
# @dp.message_handler(content_types=['photo'], state=PhotoState.photos)
# async def get_photo(message: types.Message, state, photo_description=None):
#     file_info = await bot.get_file(message.photo[-1].file_id)
#     if os.path.exists(f'UserFiles/Photos/' + file_info.file_unique_id + '.jpg'):
#         pass
#     else:
#         await message.photo[-1].download('UserFiles/Photos/' + file_info.file_unique_id + '.jpg')
#
#     await message.answer_photo(open(f'UserFiles/Photos/{file_info.file_unique_id}' + '.jpg', 'rb'),
#                                caption='Напишите подпись к следующей фотографии:')
#     await state.update_data(photos=file_info)
#     await PhotoState.description.set()
#
#         # await state.update_data(photos=photos)
#         # await message.answer(f'{len(photos)} фото загружено!')
#         # await PhotoState.description.set()
#         # await request_caption(message, state.update_data)
#
#
# # @dp.message_handler(state=PhotoState.description)
# # async def request_caption(message: types.Message, state, chat_id: int, photo_id: str, photo_description=None):
# @dp.message_handler(state=PhotoState.description)
# async def request_caption(message: types.Message, state):
#     # await message.answer('Напишите подпись к фотографии:')
#     # Запрос подписи от пользователя
#     photo_description = message.text
#     await state.update_data(description=photo_description)
#     await message.answer(f'Подпись {photo_description} загружена')
#     await PhotoState.process.set()
#
#
# @dp.message_handler(state=PhotoState.process)
# async def check(message: types.Message, state, chat_id: int, photo_id: str):
#     # Запрос подписи от пользователя
#     for value in state:
#         await message.answer(value)
#     # await message.answer(f'Подписи загружены!')
#     # await state.update_data(description=photo_description)
#     # await PhotoState.process.set()
#
#
# @dp.message_handler(content_types=['document'])
# async def handle_captions(message):
#     # Получить фото
#     photo_ids = sorted(os.listdir('photos'))
#
#     # Проверка наличия фотографий
#     if not photo_ids:
#         await message.answer('Все фотографии обработаны.')
#         return
#
#     # Получение следующей фотографии
#     current_photo_id = photo_ids[0]
#
#     # Удаление метаданных из фотографии
#     process_photo.remove_metadata(f'photos/{current_photo_id}')
#
#     # Добавление подписи к фотографии
#     process_photo.add_caption(f'photos/{current_photo_id}', message.text)
#
#     # Отправка обработанной фотографии пользователю
#     with open(f'photos/{current_photo_id}', 'rb') as photo:
#         await bot.send_photo(message.chat.id, photo)
#
#     # Удаление исходной фотографии
#     os.remove(f'photos/{current_photo_id}')


if __name__ == '__main__':
    os.makedirs('UserFiles/Photos', exist_ok=True)
    # Запуск long-polling
    executor.start_polling(dp, skip_updates=True)
