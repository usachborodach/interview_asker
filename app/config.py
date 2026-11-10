import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

    # Директория с markdown-файлами: main.md, base.md, ...
    QANDA_DIR = os.getenv('QANDA_DIR', '/root/qanda/qanda')

    # ML/RAG handbook (отдельный файл вне QANDA_DIR)
    ML_HANDBOOK_PATH = os.getenv(
        'ML_HANDBOOK_PATH',
        '/root/ML-AI-Engineer-Interview-Handbook/'
        'ultimate_ml_rag_300_interview_handbook.md',
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