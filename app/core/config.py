from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_title: str = 'Сервис анализа патентной активности компаний.'
    database_url: str

    class Config:
        env_file = '.env'


settings = Settings()
