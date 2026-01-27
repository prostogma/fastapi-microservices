from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    
    IS_TEST: bool

    # Дефолтная конфигурация
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"))

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
class TestSettings(Settings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".test.env"))


settings = Settings()  # type: ignore
