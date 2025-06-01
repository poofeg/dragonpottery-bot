from aiogram.fsm.storage.base import BaseStorage

from dragonpottery_bot.domain.order_repository import OrderRepository


class AppState:
    bot_storage: BaseStorage
    order_repository: OrderRepository


app_state = AppState()
