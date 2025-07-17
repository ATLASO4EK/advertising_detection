from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_photo_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Отправить геолокацию', request_location=True))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)