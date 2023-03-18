from apiwrapper import APIWrapper

wrapper = APIWrapper()

prices = wrapper.pair_prices()

print(prices)