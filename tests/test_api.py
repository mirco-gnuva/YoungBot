from wrappers.api_wrapper import APIWrapper
import models
import pytest

wrapper = APIWrapper()

class TestAPIWrapper:
    def test__call_200(self):
        assert wrapper._call('https://www.google.com').status_code == 200

    def test__call_404(self):
        assert wrapper._call('https://www.google.com/404').status_code == 404

class TestPairPrices:
    def test_validation(self):
        wrapper.pair_prices()
        assert True

    def test_return_type(self):
        prices = wrapper.pair_prices()
        assert isinstance(prices, models.PairPricesModel)

    def test_wrong_pair(self):
        with pytest.raises(wrapper.PairNotFound):
            wrapper.pair_prices('BTC-test')
