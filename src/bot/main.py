import logging
import asyncio

from handlers import *
from bot import *

logging.basicConfig(level=logging.INFO)
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
