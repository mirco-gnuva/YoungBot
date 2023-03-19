from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.enums import StrategyStatus

class PairPricesModel(BaseModel):
    pair: str
    open: float
    high: float
    low: float
    close: float
    bid: float
    ask: float
    percentChange: float
    baseVolume: float
    quoteVolume: float
    timestamp: int
    datetime: Optional[datetime]

    def __init__(self, **data):
        super().__init__(**data)
        self.datetime = datetime.fromtimestamp(self.timestamp/1000)


class StrategyModel(BaseModel):
    status: StrategyStatus
    instance: bytes
    metadata: str = None
    strategy_id: UUID = uuid4()

    class Config:
        use_enum_values = True

    def __init__(self, **data):
        super().__init__(**data)
        self.metadata = self.__class__.__name__


class BuyTickStrategyModel(StrategyModel):
    last_value: float
    budget: float
    tick: float
    threshold: float
    update_datetime: Optional[datetime]

    def __init__(self, **data):
        super().__init__(**data)
        self.update_datetime = datetime.now()
