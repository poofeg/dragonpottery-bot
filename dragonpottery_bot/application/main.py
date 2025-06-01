import asyncio
import logging
import sys
from pathlib import Path

import aiogram
import typer
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from dragonpottery_bot.application.app_state import app_state
from dragonpottery_bot.application.dispatcher import create_dispatcher
from dragonpottery_bot.application.settings import Settings
from dragonpottery_bot.domain.order_repository import OrderRepository
from dragonpottery_bot.infrastrucure.gspread_reader import GspreadReader

app = typer.Typer()


async def async_main(settings: Settings) -> None:
    app_state.order_repository = OrderRepository(
        GspreadReader(
            settings.gspread.service_account_filename,
            settings.gspread.spreadsheet_id,
        )
    )
    await app_state.order_repository.get_sum_by_contact()
    app_state.bot_storage = RedisStorage(Redis.from_url(str(settings.tg.redis_url)))
    bot = aiogram.Bot(
        token=settings.tg.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await create_dispatcher(app_state.bot_storage).start_polling(bot)
    await app_state.bot_storage.close()


@app.command()
def run(env_file: Path | None = None) -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    settings = Settings(_env_file=env_file)
    asyncio.run(async_main(settings))


if __name__ == "__main__":
    app()
