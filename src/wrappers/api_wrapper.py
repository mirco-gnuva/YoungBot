import requests
from requests.adapters import HTTPAdapter, Retry
from typing import Literal

from src.settings import YoungPlatformSettings, logger
from src import models

yp_settings = YoungPlatformSettings()


class APIWrapper:
    class PairNotFound(Exception):
        pass

    def __init__(self):
        logger.debug('Initializing ApiWrapper')
        logger.info('ApiWrapper initialized')

    @staticmethod
    def _call(url, method: Literal['GET'] = 'GET', max_retries: int = 3, **kwargs) -> requests.Response:
        logger.debug(f'Calling {url} with method {method} and kwargs {kwargs}')
        prefix = f"{url.split('://')[0]}://" if url.startswith('http') else 'http://'

        session = requests.Session()

        retries = Retry(total=max_retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])

        session.mount(prefix, HTTPAdapter(max_retries=retries))

        try:
            response = session.request(method, url, **kwargs)
        except requests.exceptions.RetryError as e:
            logger.error(f'{e}')
            response = requests.Response()
            response.status_code = 500

        if response.status_code >= 400:
            logger.warning(f'Got status code {response.status_code} from {url}: {response.text}')
        else:
            logger.debug(f'Got status code {response.status_code} from {url}: {response.text}')

        return response

    def pair_prices(self, pair: str = 'BTC-EUR') -> models.PairPricesModel:
        url = f'{yp_settings.host}/ticker?pair={pair}'
        response = self._call(url)

        if response.status_code == 400:
            raise self.PairNotFound(f'Pair {pair} not found')

        data = models.PairPricesModel(**response.json())

        return data
