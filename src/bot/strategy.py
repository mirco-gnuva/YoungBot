from datetime import datetime
from uuid import UUID, uuid4
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pymongo.collection import Collection
from pymongo.database import Database

import models
from src.enums import StrategyStatus
import pickle

from src.settings import logger, MongoSettings

mongo_settings = MongoSettings()


class Strategy:
    status: StrategyStatus = StrategyStatus.NEW
    _changed: bool = False
    collection: Collection
    history_collection: Collection
    strategy_id: UUID = uuid4()
    metadata: str

    def __init__(self, collection: Collection = None, history_collection: Collection = None):
        self.collection = collection
        self.history_collection = history_collection
        self.metadata = self.__class__.__name__

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def _check(self, *args, **kwargs):
        raise NotImplementedError

    def check(self, *args, **kwargs):
        self._check(*args, **kwargs)
        saved = self.save() if self._changed else self._save_to_history()

        if saved:
            logger.info(f'Strategy saved: {self.strategy_id}')
        else:
            logger.error(f'Error while saving strategy: {self.strategy_id}')



    def triggered(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    def enrich_plot(self, plot: go.Figure):
        raise NotImplementedError

    def _to_dict(self) -> dict:
        raise NotImplementedError

    def to_dict(self) -> dict:
        data = self._to_dict()
        data['status'] = self.status.value
        data['strategy_id'] = self.strategy_id
        data['metadata'] = self.metadata

        return data

    def _save_strategy(self):
        logger.debug(f'Checking if strategy exists in MongoDB: {self.strategy_id}')
        exists = self.collection.count_documents({'strategy_id': self.strategy_id}) > 0

        data = self.to_dict()

        if exists:
            logger.debug(f'Strategy exists in MongoDB, updating: {self.strategy_id}')
            result = self.collection.update_one({'strategy_id': self.strategy_id}, {'$set': data})
        else:
            logger.debug(f'Strategy does not exist in MongoDB, inserting: {self.strategy_id}')
            result = self.collection.insert_one(data)

        if result.acknowledged:
            logger.debug(f'Strategy saved to MongoDB: {self.strategy_id}')
            self._changed = False
        else:
            logger.error(f'Error while saving strategy to MongoDB: {self.strategy_id}')

        return result.acknowledged

    def _save_to_history(self):
        data = self.to_dict()
        data['timestamp'] = datetime.now().timestamp() * 1000
        data['datetime'] = datetime.now()

        logger.debug(f"Saving strategy's data to history: {self.strategy_id}")
        result = self.history_collection.insert_one(data)

        if result.acknowledged:
            logger.debug(f'Strategy saved to MongoDB: {self.strategy_id}')
            self._changed = False
        else:
            logger.error(f'Error while saving strategy to MongoDB: {self.strategy_id}')

        return result.acknowledged

    def save(self) -> bool:
        logger.debug(f'Saving strategy to MongoDB: {self}')

        latest_status_saved = self._save_strategy()
        history_status_saved = self._save_to_history()

        return latest_status_saved and history_status_saved

    def _load(self, data: dict):
        raise NotImplementedError

    def load(self, data: dict, collection: Collection, history_collection: Collection):
        self._load(data)
        self.collection = collection
        self.history_collection = history_collection
        self.strategy_id = data['strategy_id']
        self.status = StrategyStatus(data['status'])


class BuyTickStrategy(Strategy):
    last_value: float = None

    def __init__(self, tick: float = None, budget: float = None, collection: Collection = None, history_collection: Collection = None):
        super().__init__(collection, history_collection)
        self.budget = budget
        self.tick = tick

    def __str__(self):
        return f'{self.last_value}'

    def _check(self, prices: models.PairPricesModel):
        if self.last_value is None:
            self.last_value = prices.close
            self._changed = True
        elif self.triggered(prices):
            logger.debug(f'Strategy triggered: {self} with price {prices.close}')
            self.status = StrategyStatus.TRIGGERED
            self.run()
            self._changed = True
        elif self.status not in [StrategyStatus.COMPLETED, StrategyStatus.FAILED]:
            self._changed = self.update(prices)

    def triggered(self, prices: models.PairPricesModel) -> bool:
        return prices.close >= self.threshold

    @property
    def threshold(self) -> float:
        return self.last_value + self.tick

    def update(self, prices: models.PairPricesModel) -> bool:
        """If latest price is lower than the last value, update it and return True, otherwise return False.

        Parameters
        ----------
        prices : models.PairPricesModel
            Latest prices

        Returns
        -------
        bool
            True if last value was updated, False otherwise
        """

        if prices.close < self.last_value:
            logger.debug(f'Updating last value from {self.last_value} to {prices.close}')
            self.last_value = prices.close
            return True
        return False

    def run(self):
        self.status = StrategyStatus.RUNNING
        logger.debug(f'Running strategy: {self}')
        # TODO: implement buy logic
        self.status = StrategyStatus.COMPLETED

    def enrich_plot(self, plot: go.Figure):
        if self.last_value:
            plot.add_hrect(y0=self.last_value, y1=self.threshold, line_width=0, fillcolor='green', opacity=0.25)

        history = self.history_collection.find({'strategy_id': self.strategy_id})
        history_df = pd.DataFrame(history)
        if not history_df.empty:
            plot.add_scatter(x=history_df['datetime'], y=history_df['last_value'], line_color='green', name=str(self))


    def _load(self, data: dict):
        self.last_value = data['last_value']
        self.budget = data['budget']
        self.tick = data['tick']

    def _to_dict(self) -> dict:
        data = {'last_value': self.last_value,
                'budget': self.budget,
                'tick': self.tick}
        return data


factory = {'BuyTickStrategy': BuyTickStrategy}
