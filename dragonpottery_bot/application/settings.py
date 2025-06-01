from pathlib import Path

from pydantic import BaseModel, SecretStr, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Telegram(BaseModel):
    token: SecretStr
    redis_url: RedisDsn = RedisDsn('redis://')


class Gspread(BaseModel):
    spreadsheet_id: str
    service_account_filename: Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__', nested_model_default_partial_update=True
    )

    tg: Telegram
    gspread: Gspread
