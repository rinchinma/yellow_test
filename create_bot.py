from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()

bot = Bot(token='5747298356:AAFSYVDvMK31bAta_KQNRpRuNJxE8yJPamQ')
dp = Dispatcher(bot, storage=storage)
