from uuid import UUID, uuid4

from plotly.graph_objects import Figure
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
    strategy_id: UUID = uuid4()
    metadata: str

    def __init__(self, collection: Collection):
        self.collection = collection
        self.metadata = self.__class__.__name__

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def check(self, *args, **kwargs):
        raise NotImplementedError

    def triggered(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    def enrich_plot(self, plot: Figure):
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    def save(self) -> bool:
        logger.debug(f'Saving strategy to MongoDB: {self}')
        logger.debug(f'Checking if strategy exists in MongoDB: {self.strategy_id}')
        exists = self.collection.find({'strategy_id': self.strategy_id}).count() > 0

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

        return result.acknowledged

    def load(self, data: dict):
        raise NotImplementedError


class BuyTickStrategy(Strategy):
    last_value: float = None

    def __init__(self, tick: float, budget: float, collection: Collection):
        super().__init__(collection)
        self.budget = budget
        self.tick = tick

    def check(self, prices: models.PairPricesModel):
        if self.triggered(prices):
            logger.debug(f'Strategy triggered: {self} with price {prices.close}')
            self.status = StrategyStatus.TRIGGERED
            self.run()
            self._changed = True
        elif self.status not in [StrategyStatus.RUNNING, StrategyStatus.COMPLETED, StrategyStatus.FAILED]:
            self._changed = self.update(prices)

        if self._changed:
            self.save()

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
        # TODO: Uncomment
        # self.status = StrategyStatus.COMPLETED

    def enrich_plot(self, plot: Figure):
        plot.add_hrect(y0=self.last_value, y1=self.threshold, line_width=0, fillcolor='green', opacity=0.25,
                       annotation=str(self))

    def load(self, data: dict):
        self.last_value = data['last_value']
        self.budget = data['budget']
        self.tick = data['tick']
        self.strategy_id = data['strategy_id']
        self.status = data['status']

    def to_dict(self) -> dict:
        data = {'strategy_id': self.strategy_id,
                'status': self.status,
                'last_value': self.last_value,
                'budget': self.budget,
                'tick': self.tick}
        return data
