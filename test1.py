import asyncio

import telebot.types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import download_file
from telebot import types

from exif import Image





bot = AsyncTeleBot('8171844045:AAFTmhKK0e49WclAgHtQRAlzLt3s9Gj1j3E')


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    text = 'Привет, я тестовый пидорас, отправь мне фото и я пошлю тебя нахуй'
    await bot.reply_to(message, text, reply_markup=keyboard)

#keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#keyboard.add(types.KeyboardButton('/start'), types.KeyboardButton('/help'))
#@bot.message_handler(commands=['help'])
#async def handle_help(message):
#    await bot.send_message(message.chat.id, "Вот доступные команды:", reply_markup=keyboard)

keyboard = types.InlineKeyboardMarkup()
button_report = types.InlineKeyboardButton(text='Отправить изображение на проверку', callback_data='rep_data')

@bot.callback_query_handler(func=lambda call: call.data == 'rep_data')
def rep_data(call):




@bot.message_handler(func=lambda message: True)
async def echo_message(message):
   await bot.send_message(message.chat.id, 'иди нахуй')

@bot.message_handler(content_types=['photo'])
async def new_massage(message: telebot.types.Message):
    result_message = await bot.send_message(message.chat.id, 'Скачиваем вашу хуйню')
    file_path = await bot.get_file(message.photo[-1].file_id)
    downloaded_file = await bot.download_file(file_path.file_path)
    with open('file.jpg', 'wb') as new_file:
        new_file.write(downloaded_file)

    await bot.edit_message_text(chat_id=message.chat.id, message_id=result_message.id, text='Иди нахуй')
    with open('file.jpg', 'rb') as file:
        img = Image(file)
        if img.has_exif:
            status = f"contains EXIF (version {img.exif_version}) information."
        else:
            status = "does not contain any EXIF information."
        print(status)






asyncio.run(bot.polling())