from pymongo import MongoClient
import urllib

from src.settings import MongoSettings, logger

mongo_settings = MongoSettings()

def get_client():
    url = f'mongodb://{mongo_settings.db_user}:{urllib.parse.quote(mongo_settings.db_password)}@{mongo_settings.db_host}:{mongo_settings.db_port}/{mongo_settings.db_database}'
    logger.debug(f'Connecting to MongoDB at {mongo_settings.db_host}:{mongo_settings.db_port}')
    client = MongoClient(url)
    return client

def get_database():
    client = get_client()
    return client[mongo_settings.db_database]