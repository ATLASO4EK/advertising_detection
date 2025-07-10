import asyncio

import telebot.types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import download_file
from telebot import types
import json
from exif import Image


bot = AsyncTeleBot('8171844045:AAFTmhKK0e49WclAgHtQRAlzLt3s9Gj1j3E')


with open("tg_ids.json", "r", encoding="utf-8") as file:
    whitelist = json.load(file)
print(whitelist)


def decorator(func):
    async def blablabla(message):
        user_id = message.from_user.id
        print(user_id)
        if user_id in whitelist:
            await func(message)
        else:
            await bot.reply_to(message, "Иди нахуй.")
    return blablabla


@bot.message_handler(commands=['start'])
@decorator
async def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup()
    button_report = types.InlineKeyboardButton(text='Создать обращение по вандализму', callback_data='rep_data')
    keyboard.add(button_report)
    text = 'Привет, я тестовый пидорас, отправь мне фото и я пошлю тебя нахуй'
    await bot.send_message(message.from_user.id, text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'rep_data')
async def rep_data(call):
    message = call.message
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Отправьте изображение вандализма')

    @bot.message_handler(content_types=['photo'])
    async def new_massage(message1: telebot.types.Message):
        result_message = await bot.send_message(message1.chat.id, 'Скачиваем вашу хуйню')
        file_path = await bot.get_file(message1.photo[-1].file_id)
        downloaded_file = await bot.download_file(file_path.file_path)
        with open('file.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)
        await bot.edit_message_text(chat_id=message1.chat.id, message_id=result_message.id, text='Иди нахуй')
        keyboard_loc = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        loc_button = types.KeyboardButton(text='Поделиться геолокацией', request_location=True)
        keyboard_loc.add(loc_button)
        await bot.send_message(chat_id=message1.chat.id, text='Поделитесь геолокацией', reply_markup=keyboard_loc)


@bot.callback_query_handler(func=lambda call: call.data == 'loc_data')
async def loc_data(call):

    message = call.message
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Отправьте изображение вандализма')


@bot.message_handler(content_types=['location'])
async def handle_location(message):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        remove_keyboard = types.ReplyKeyboardRemove()
        print(f"Получены координаты:\nШирота: {lat}\nДолгота: {lon}")
        await bot.send_message(message.chat.id, f"Получены координаты:\nШирота: {lat}\nДолгота: {lon}", reply_markup=remove_keyboard)
        await bot.send_message(message.chat.id, 'Обращение создано')
        await send_welcome(message)


if __name__ == '__main__':
    asyncio.run(bot.polling())