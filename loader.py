import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from utils.db_api.sklad import Sklad
from utils.db_api.baza_ludi import Database
from utils.db_api.zakaz import Zakaz

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

loop = asyncio.get_event_loop()
db = loop.run_until_complete(Database.create())
com=loop.run_until_complete(Sklad.create())
op=loop.run_until_complete(Zakaz.create())

