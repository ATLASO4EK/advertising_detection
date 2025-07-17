from aiogram import Bot, Dispatcher, types, F
from config import API_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)