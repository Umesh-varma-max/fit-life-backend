# config.py
import os
from datetime import timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration — shared by all environments."""

    @staticmethod
    def _parse_origins(raw_value: str):
        """Allow a single origin or a comma-separated list of origins."""
        origins = [origin.strip() for origin in (raw_value or '').split(',') if origin.strip()]
        if not origins:
            return ['http://localhost:3000']
        return origins if len(origins) > 1 else origins[0]

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

    if DATABASE_URL:
        # Neon/Render commonly provide a postgres-style URL.
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
                'postgres://', 'postgresql+psycopg://', 1
            )
        elif SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
                'postgresql://', 'postgresql+psycopg://', 1
            )
    else:
        # Backward-compatible fallback for local DB settings.
        DB_DIALECT = os.getenv('DB_DIALECT', 'postgresql+psycopg')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'fitness_db')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = quote_plus(os.getenv('DB_PASSWORD', ''))

        SQLALCHEMY_DATABASE_URI = (
            f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    FRONTEND_ORIGIN = _parse_origins.__func__(os.getenv(
        'FRONTEND_ORIGIN',
        'http://localhost:3000,https://fitlife-frontend.onrender.com,https://fit-life-frontend.vercel.app'
    ))


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)


# Map string name to class (used in app.py)
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
