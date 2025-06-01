import re
from collections.abc import AsyncIterable
from pathlib import Path
from typing import Any

from google.oauth2.service_account import Credentials
from gspread.utils import ValueRenderOption, ValueInputOption
from gspread_asyncio import AsyncioGspreadClientManager, AsyncioGspreadSpreadsheet


class GspreadReader:
    def __init__(self, service_account_filename: Path, spreadsheet_id: str) -> None:
        self.__service_account_filename = service_account_filename
        self.__spreadsheet_id = spreadsheet_id
        self.__agcm = AsyncioGspreadClientManager(self.__get_creds)
        self.__spreadsheet: AsyncioGspreadSpreadsheet | None = None

    def __get_creds(self) -> Credentials:
        creds = Credentials.from_service_account_file(str(self.__service_account_filename.resolve()))
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped

    async def __get_spreadsheet(self) -> AsyncioGspreadSpreadsheet:
        if not self.__spreadsheet:
            agc = await self.__agcm.authorize()
            self.__spreadsheet = await agc.open_by_key(self.__spreadsheet_id)
        return self.__spreadsheet

    async def read_all_worksheets(self, except_regex: str) -> AsyncIterable[list[dict[str, Any]]]:
        ss = await self.__get_spreadsheet()
        worksheets = await ss.worksheets()
        for worksheet in worksheets:
            if re.match(except_regex, worksheet.title):
                continue
            yield await worksheet.get_all_records(value_render_option=ValueRenderOption.unformatted)

    async def read_worksheet(self, title: str) -> list[dict[str, Any]]:
        ss = await self.__get_spreadsheet()
        worksheet = await ss.worksheet(title)
        return await worksheet.get_all_records(value_render_option=ValueRenderOption.unformatted)

    async def append_row(self, title: str, row: list[str | float]) -> None:
        ss = await self.__get_spreadsheet()
        worksheet = await ss.worksheet(title)
        await worksheet.append_row(row, ValueInputOption.user_entered)
