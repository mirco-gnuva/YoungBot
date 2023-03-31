import threading
from time import sleep
import pickle

from src import models
from src.wrappers.api_wrapper import APIWrapper
from src.settings import logger, Settings, MongoSettings
from src.wrappers.db_wrapper import get_database
from src.bot import strategy
from src.enums import StrategyStatus

settings = Settings()
mongo_settings = MongoSettings()

wrapper = APIWrapper()
db = get_database()


def save_pair_close_price(prices: models.PairPricesModel):
    logger.debug(f'Going to save prices to MongoDB: {prices}')
    result = db[mongo_settings.db_price_collection].insert_one(prices.dict())

    if not result.acknowledged:
        logger.error('Error while inserting data to MongoDB')
    else:
        logger.debug(f'Data inserted to MongoDB: {result.inserted_id}')


def get_running_strategies():
    logger.debug('Getting running strategies')
    collection = db[mongo_settings.db_strategy_collection]
    history_collection = db[mongo_settings.db_strategy_history_collection]
    results = collection.find({'status': {'$in': [StrategyStatus.RUNNING.value, StrategyStatus.NEW.value]}})
    results = list(results)
    strategies = [strategy.factory[result['metadata']]() for result in results]
    [st.load(data, collection, history_collection) for st, data in zip(strategies, results)]
    return strategies


def start_loop():
    logger.info('Starting main loop')
    while True:
        logger.debug('Starting new iteration')
        prices = wrapper.pair_prices()
        threading.Thread(target=save_pair_close_price, args=(prices,)).start()

        strategies = get_running_strategies()

        # TODO: convert to async
        for strategy in strategies:
            strategy.check(prices)

        logger.debug(f'Going to sleep for {settings.LOOP_INTERVAL} seconds')
        sleep(settings.LOOP_INTERVAL)
