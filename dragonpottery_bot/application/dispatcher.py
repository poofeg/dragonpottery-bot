from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseStorage

from dragonpottery_bot.application.forms import start


def create_dispatcher(bot_storage: BaseStorage) -> Dispatcher:
    dp = Dispatcher(storage=bot_storage)
    dp.include_router(start.router)
    return dp
