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
    results = db[mongo_settings.db_strategy_collection].find({'status': {'$in': [StrategyStatus.RUNNING.value, StrategyStatus.NEW.value]}})
    strategies = [pickle.loads(result['instance']) for result in results]
    return strategies


def save_strategy(strategy: strategy.Strategy) -> bool:
    model = strategy.as_model()

    exists = db[mongo_settings.db_strategy_collection].find({'strategy_id': model.strategy_id}).count() > 0
    
    if exists:
        result = db[mongo_settings.db_strategy_collection].update_one({'strategy_id': model.strategy_id})

    logger.debug(f'Going to save strategy to MongoDB: {strategy}')
    result = db[mongo_settings.db_strategy_collection].insert_one(model.dict())
    return result.acknowledged


def start_loop():
    logger.info('Starting main loop')
    while True:
        logger.debug('Starting new iteration')
        prices = wrapper.pair_prices()
        threading.Thread(target=save_pair_close_price, args=(prices,)).start()

        strategies = get_running_strategies()

        for strategy in strategies:
            strategy.check(prices)
            if strategy.changed:
                save_strategy(strategy)
                strategy.mark_saved()

        logger.debug(f'Going to sleep for {settings.LOOP_INTERVAL} seconds')
        sleep(settings.LOOP_INTERVAL)
