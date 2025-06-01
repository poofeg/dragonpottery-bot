from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from dragonpottery_bot.application.forms import start


def create_dispatcher(bot_storage: BaseStorage) -> Dispatcher:
    dp = Dispatcher(storage=bot_storage)
    dp.include_router(start.router)

    i18n = I18n(path='locales', default_locale='en', domain='messages')
    i18n_middleware = SimpleI18nMiddleware(i18n)
    dp.update.middleware(i18n_middleware)

    return dp
