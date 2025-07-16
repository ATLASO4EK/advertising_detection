from aiogram import Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ALLOWED_USERS
from states import *
from keyboards import *
from api import *
from bot import bot, dp

# Декоратор для проверки user_id в ALLOWED_USERS
from functools import wraps
def whitelist_only(handler):
    @wraps(handler)
    async def wrapper(message: types.Message, *args, **kwargs):
        user_id = message.from_user.id
        if user_id not in ALLOWED_USERS:
            print(user_id)
            await message.answer('Извините, вас нет в базе')
            return
        return await handler(message, *args, **kwargs)
    return wrapper


@dp.message(Command('start'))
@whitelist_only
async def handle_start(message: types.Message, state: FSMContext):
    try:
        await state.set_state(MainMenuStates.MAIN)
        await message.answer('Добро пожаловать! Нажмите кнопку ниже, чтобы прислать геолокацию и фото.',
                             reply_markup=get_photo_keyboard())
    except Exception as e:
        await message.answer(f'Ошибка: {e}')
        assert False, f'Ошибка в handle_start: {e}'

@dp.message(F.photo)
@whitelist_only
async def handle_photo(message: types.Message, bot: Bot, state: FSMContext):
    try:
        current_state = await state.get_state()
        if current_state != MainMenuStates.WAIT_PHOTO.state:
            await message.answer('Сначала отправьте геолокацию.')
            return
        user_id = message.from_user.id
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file.file_path)
        # Получаем координаты из state, если они были отправлены ранее
        data = await state.get_data()
        lat = data.get('lat')
        lon = data.get('lon')
        response = send_photo_to_api(user_id, file_bytes, lat, lon)
        post_ticket(user_id, file_bytes, lat, lon)

        await message.answer('Запрос на очистку создан! ✅'
                                 'Благодарим, что заботитесь о чистоте нашего города!\n '
                                 'Теперь Вы можете отправить еще один объект =)', reply_markup=get_photo_keyboard())

        # После отправки фото возвращаемся в MAIN
        await state.set_state(MainMenuStates.MAIN)
        await state.update_data(lat=None, lon=None)
    except Exception as e:
        await message.answer(f'Ошибка: {e}')
        assert False, f'Ошибка в handle_photo: {e}'

@dp.message(F.location)
@whitelist_only
async def handle_location(message: types.Message, state: FSMContext):
    try:
        await state.set_state(MainMenuStates.WAIT_PHOTO)
        user_id = message.from_user.id
        lat = message.location.latitude
        lon = message.location.longitude
        # Сохраняем координаты в state
        await state.update_data(lat=lat, lon=lon)
        await message.answer(f'Геолокация получена! Широта: {lat}, Долгота: {lon}. Теперь отправьте фото.')
    except Exception as e:
        await message.answer(f'Ошибка: {e}')
        assert False, f'Ошибка в handle_location: {e}'

@dp.message(F.content_type.in_(['document', 'audio', 'video', 'voice', 'sticker']))
@whitelist_only
async def handle_other(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        if current_state == MainMenuStates.WAIT_PHOTO.state:
            await message.answer('Пришлите изображение.')
        else:
            await message.answer('Пожалуйста, выберите действие из меню.')
    except Exception as e:
        await message.answer(f'Ошибка: {e}')
        assert False, f'Ошибка в handle_other: {e}'