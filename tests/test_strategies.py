import pandas as pd
from random import randint
import plotly.express as px

from src.bot.strategy import BuyTickStrategy
from src.enums import StrategyStatus
from src.wrappers import api_wrapper


class TestBuyTickStrategy:
    def test_simulation(self):
        states = []

        wrapper = api_wrapper.APIWrapper()

        prices = wrapper.pair_prices()
        prices.close = 500

        strategy = BuyTickStrategy(prices=prices, tick=5, budget=100)

        state = {'close': prices.close, 'last_value':strategy.last_value , 'threshold': strategy.threshold, 'status': strategy.status}
        states.append(state)

        for i in range(1000):
            prices.close = prices.close + randint(-10, 10)

            if prices.close > strategy.threshold:
                assert strategy.triggered(prices)

            old_value = strategy.last_value

            strategy.check(prices)
            state = {'close': prices.close, 'last_value': strategy.last_value , 'threshold': strategy.threshold, 'status': strategy.status}
            states.append(state)

            if strategy.status not in [StrategyStatus.COMPLETED, StrategyStatus.FAILED]:
                if prices.close < old_value:
                    assert strategy.last_value == prices.close
                    assert strategy.status != StrategyStatus.RUNNING
                elif prices.close >= strategy.threshold:
                    assert strategy.status == StrategyStatus.COMPLETED

            assert strategy.threshold - strategy.last_value == strategy.tick

        df = pd.DataFrame(states)

        fig = px.line(df, x=df.index, y=['close', 'last_value', 'threshold'])

        fig.write_image('TestBuyTickStrategy_test_simulation.png', width=1920, height=1080)

