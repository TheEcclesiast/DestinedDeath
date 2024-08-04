import logging

from aiogram import Bot, Dispatcher
import os
import asyncio


from settings import *



from Handlers import handlers_router
from database import Posts
from FSM import all_fsm_routers




bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()
dp.include_routers(handlers_router, all_fsm_routers)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_bot():
    print('Database is ', end='')
    try:
        Posts.create_table()
        print('Ok')


    except:
        print('Failure')
    dp.startup.register(on_start)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(start_bot())

