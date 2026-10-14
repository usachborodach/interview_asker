import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

    # Путь к файлу со списком вопросов
    LIST_MD_PATH = os.getenv('LIST_MD_PATH', str(BASE_DIR / 'list.md'))

    # Базовый URL, к которому добавляется anchor из list.md
    ANSWER_BASE_URL = os.getenv(
        'ANSWER_BASE_URL',
        'https://github.com/Swfuse/devops-interview/blob/main/interview.md',
    )

    RATELIMIT_DEFAULT = "120 per minute"
    RATELIMIT_STORAGE_URI = "memory://"


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


_CONFIGS = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': Config,
}


def get_config(name: str | None = None):
    if name is None:
        name = os.getenv('FLASK_ENV', 'default')
    return _CONFIGS.get(name, Config)