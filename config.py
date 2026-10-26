import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'anitrack-anime-super-secret-key-2026')
    DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'anitrack.db'))
    TESTING = False
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    DATABASE = os.environ.get('TEST_DATABASE_PATH', os.path.join(BASE_DIR, 'test_anitrack.db'))
