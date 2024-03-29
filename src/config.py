# /src/config.py

import os

class Development(object):
    """
    Development environment configuration
    """
    DEBUG = True
    TESTING = False
    JWT_SECRET_KEY = os.getenv('BIZI_HASHING_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('BIZI_DATABASE_URL')

class Production(object):
    """
    Production environment configurations
    """
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('BIZI_DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('BIZI_HASHING_KEY')

app_config = {
    "development": Development,
    "production": Production,
}
