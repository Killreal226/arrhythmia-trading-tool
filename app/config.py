import json

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file="config.env")

    API_TOKEN: str  # токен для работы с API тинькофа
    ID_ACCOUNT: str  # id моего аккаунта из запроса client.users.get_accounts()

    DEPTH_ORDER_BOOK: int

    DB_HOST: str  # localhost или IP сервера
    DB_PORT: int  # Порт 3306 по дефолту
    DB_USERNAME: str  # Имя Пользователя БД
    DB_PASSWORD: str  # Пароль от БД
    DB_NAME: str  # Имя базы данных

    LOG_FILE: str  # Путь к файлу для записи логов

    DATA_TICKERS: dict = {}

    @property
    def DATABASE_URL(self):
        return f"mysql+aiomysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def load_data_tickers(self):
        with open("data_tickers.json", "r") as f:
            self.DATA_TICKERS = json.load(f)


config = Config()
config.load_data_tickers()

logger.add(config.LOG_FILE, rotation="1024 MB", level="INFO")
