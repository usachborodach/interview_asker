import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    MONGO_DB = os.getenv('MONGO_DB', 'interview_asker')
    MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'qanda')

    # ML/RAG handbook (markdown)
    ML_HANDBOOK_PATH = os.getenv(
        'ML_HANDBOOK_PATH',
        '/root/ML-AI-Engineer-Interview-Handbook/ultimate_ml_rag_300_interview_handbook.md',
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