from decouple import config
from datetime import timedelta


class Config:
    SECRET_KEY = config('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = "mongodb://localhost:27017/web-aggregator"
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379


class DevConfig(Config):
    CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
    DEBUG = True

class ProConfig(Config):
    DEBUG = False
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
