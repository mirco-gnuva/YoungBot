from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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