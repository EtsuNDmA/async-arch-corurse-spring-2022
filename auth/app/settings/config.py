from enum import Enum

from pydantic import BaseSettings


class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppSettings(BaseSettings):
    LOG_LEVEL: LogLevelEnum = LogLevelEnum.DEBUG
    AIOKAFKA_LOG_LEVEL: LogLevelEnum = LogLevelEnum.INFO

    DEBUG: bool = False

    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str = "postgresql"
    PG_PORT: int = 5432
    PG_DB: str

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_USER_STREAMING_TOPIC: str

    SECRET_KEY: str  # To generate SECRET_KEY use `openssl rand -hex 32`
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    @property
    def database_connection_url(self):
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    class Config:
        env_file = f"app/settings/.env"


settings = AppSettings()
