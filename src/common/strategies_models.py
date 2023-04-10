from pymongo.collection import Collection
from typing import Annotated, Union
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
import math

from common.enums import StrategyStatus


class Strategy(BaseModel):
    status: StrategyStatus
    metadata: str
    strategy_id: UUID = uuid4()

    def __init__(self, **data):
        super().__init__(**data)
        self.metadata = self.__class__.__name__


class TickStrategy(Strategy):
    activation: float
    default_activation: float
    tick: float
    budget: float
    last_value: float = None


class BuyTickStrategy(TickStrategy):
    default_activation = math.inf


class SellTickStrategy(TickStrategy):
    default_activation = 0.0


AbstractStrategy = Annotated[Union[Strategy, TickStrategy], Field(discriminator='metadata')]
