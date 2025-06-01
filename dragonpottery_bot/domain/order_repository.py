import logging
import re
from collections import defaultdict
from datetime import datetime, timezone
from operator import itemgetter
from zoneinfo import ZoneInfo

from dragonpottery_bot.infrastrucure.gspread_reader import GspreadReader

logger = logging.getLogger(__name__)


class OrderRepository:
    RE_NOT_DIGIT = re.compile(r'\D')
    RE_PHONE_NUMBER = re.compile(r'^\d{7,15}$')
    RE_RUSSIAN_8 = re.compile(r'^8(\d{10})$')

    def __init__(self, gspread_reader: GspreadReader) -> None:
        self.__gspread_reader = gspread_reader
        self.__sum_by_contact: dict[str, float] | None = None

    async def get_sum_by_contact(self, update: bool = False) -> dict[str, float]:
        if self.__sum_by_contact and not update:
            return self.__sum_by_contact
        logger.info('Update sum by contact')
        result: defaultdict[str, float] = defaultdict(float)
        async for ws in self.__gspread_reader.read_all_worksheets(except_regex=r'^!'):
            for row in ws:
                phone = str(row['Телефон'])
                if not phone:
                    continue
                phone = self.RE_NOT_DIGIT.sub('', phone.split('\n')[0])
                if not self.RE_PHONE_NUMBER.match(phone):
                    logger.warning('Invalid phone: %r', row['Телефон'])
                    continue
                if m := self.RE_RUSSIAN_8.match(phone):
                    phone = f'7{m.group(1)}'
                try:
                    order_sum = float(row['Сумма'])
                except ValueError:
                    if row['Сумма']:
                        logger.warning('Invalid sum: %r', row['Сумма'])
                    order_sum = 0.0
                result[phone] += order_sum
        logger.info('Sum by contact updated')
        self.__sum_by_contact = result
        return result

    async def calc_discount(self, orders_sum: float) -> tuple[str, float]:
        ws = await self.__gspread_reader.read_worksheet('! Промокоды !')
        ws = sorted(ws, key=itemgetter('Сумма'), reverse=True)
        for row in ws:
            if orders_sum >= row['Сумма']:
                return row['Промокод'], row['Скидка, %']
        return '', 0.0

    async def save_issue(self, phone_number: str, orders_sum: float, code: str) -> None:
        await self.__gspread_reader.append_row(
            title='! Выданные промокоды !',
            row=[
                datetime.now(tz=ZoneInfo('Europe/Moscow')).replace(tzinfo=None).isoformat(timespec='seconds'),
                f'\'+{phone_number}',
                orders_sum,
                code
            ],
        )
