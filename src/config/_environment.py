from pydantic_settings import BaseSettings
from os import getcwd
from os.path import exists, join
from dotenv import load_dotenv


class Environment(BaseSettings):
    TYPESENSE_API_KEY: str
    TYPESENSE_HOST: str
    TYPESENSE_PORT: str
    TYPESENSE_PROTOCOL: str
    LOG_LEVEL: str
    QDRANT_URL: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @classmethod
    def from_env_file(cls, env_file: str | None = None):
        """특정 환경 파일에서 설정을 로드합니다."""
        if env_file is None:
            env_file = join(getcwd(), ".env")

        if exists(env_file):
            load_dotenv(env_file)

        return cls()
