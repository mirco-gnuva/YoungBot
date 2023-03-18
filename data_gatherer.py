from time import sleep

from apiwrapper import APIWrapper
from settings import logger, Settings, MongoSettings
from db_wrapper import get_database

settings = Settings()
mongo_settings = MongoSettings()

wrapper = APIWrapper()
db = get_database()


def start_loop():
    logger.info('Starting main loop')
    while True:
        logger.debug('Starting new iteration')
        prices = wrapper.pair_prices()

        result = db[mongo_settings.db_price_collection].insert_one(prices.dict())

        if not result.acknowledged:
            logger.error('Error while inserting data to MongoDB')
        else:
            logger.debug(f'Data inserted to MongoDB: {result.inserted_id}')

        logger.debug(f'Going to sleep for {settings.LOOP_INTERVAL} seconds')
        sleep(settings.LOOP_INTERVAL)
