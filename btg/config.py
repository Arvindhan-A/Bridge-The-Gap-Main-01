import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


DEFAULT_SECRET_KEY = 'change-this-in-production'


class Config:
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)

    # Support PostgreSQL (production) and SQLite (development)
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    if DATABASE_URL:
        # Render, Heroku, etc. use postgres:// but SQLAlchemy needs postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'data', 'btg.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 40 * 1024 * 1024
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Seed credentials (used if DB is empty)
    SEED_ADMIN_EMAIL = os.environ.get('BTG_ADMIN_EMAIL', 'admin@bridgethegaprobotics.org')
    SEED_ADMIN_PASSWORD = os.environ.get('BTG_ADMIN_PASSWORD', '')
    SEED_PRESIDENT_PASSWORD = os.environ.get('BTG_PRESIDENT_PASSWORD', '')

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Rate limiting
    LOGIN_RATE_LIMIT = 5
    LOGIN_RATE_WINDOW = 60


class ProductionConfig(Config):
    """Production configuration - used when FLASK_ENV=production."""
    DEBUG = False
    TESTING = False

    # Stricter session cookie for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


def get_config():
    """Select a config class based on FLASK_ENV (defaults to development)."""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    if env == 'production':
        if Config.SECRET_KEY == DEFAULT_SECRET_KEY:
            raise RuntimeError(
                'Refusing to start with FLASK_ENV=production and the default SECRET_KEY. '
                'Set a strong SECRET_KEY in your environment.'
            )
        if not Config.SEED_ADMIN_PASSWORD:
            raise RuntimeError(
                'Refusing to start with FLASK_ENV=production without BTG_ADMIN_PASSWORD set. '
                'Set it in your environment before first run.'
            )
        return ProductionConfig
    if env == 'testing':
        return TestingConfig
    return DevelopmentConfig
