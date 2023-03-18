from time import sleep

from apiwrapper import APIWrapper
from settings import logger, Settings

wrapper = APIWrapper()
settings = Settings()

logger.info('Starting main loop')
while True:
    logger.debug('Starting new iteration')
    prices = wrapper.pair_prices()

    logger.debug(f'Going to sleep for {settings.LOOP_INTERVAL} seconds')
    sleep(settings.LOOP_INTERVAL)

