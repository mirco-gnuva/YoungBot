from typing import Union

from fastapi import FastAPI, status
from common.strategies_models import BuyTickStrategy, SellTickStrategy

app = FastAPI()


@app.post("/strategy/tick", status_code=status.HTTP_200_OK)
def add_buy_tick_strategy(strategy: Union[BuyTickStrategy, SellTickStrategy]):
    return {'message': 'ok'}, 200
