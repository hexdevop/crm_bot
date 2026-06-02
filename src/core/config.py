from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Настройки логирования
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Настройки приложения
    ENV: Literal["dev", "staging", "prod"] = "dev"
    BOT_TOKEN: SecretStr
    username: Optional[str] = None
    ADMIN_IDS: list[int] = []
    SKIP_UPDATES: bool = False

    # Настройки вебхука
    USE_WEBHOOK: bool = False
    WEBHOOK_URL: str = "https://example.com"
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_SECRET: SecretStr = SecretStr("secret")

    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8080

    # Настройки ngrok (для локальной разработки)
    USE_NGROK: bool = False
    NGROK_AUTHTOKEN: Optional[SecretStr] = None
    NGROK_DOMAIN: Optional[str] = None

    @property
    def webhook_url(self) -> str:
        return f"{self.WEBHOOK_URL}{self.WEBHOOK_PATH}"

    # Настройки базы данных
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASS: SecretStr
    DB_NAME: str = "bot_db"

    @property
    def database_url(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Настройки Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASS: SecretStr | None = None

    REDIS_DB_FSM: int = 0
    REDIS_DB_CACHE: int = 1
    REDIS_DB_JOB: int = 2

    def _build_redis_url(self, db: int) -> str:
        auth = f":{self.REDIS_PASS.get_secret_value()}@" if self.REDIS_PASS else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"

    @property
    def redis_fsm_url(self) -> str:
        return self._build_redis_url(self.REDIS_DB_FSM)

    @property
    def redis_cache_url(self) -> str:
        return self._build_redis_url(self.REDIS_DB_CACHE)

    @property
    def redis_job_url(self) -> str:
        return self._build_redis_url(self.REDIS_DB_JOB)

    # Настройки производительности
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 30


settings = Settings()
