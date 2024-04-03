import numpy as np
import statistics
from src.trading_strategies.financial_asset.price import Price
from src.trading_strategies.financial_asset.symbol import Symbol


class Stock:
    def __init__(self, stock_symbol: Symbol, current_price: Price,
                 historical_price: [Price]):
        self.stock_symbol = stock_symbol
        self.current_price = current_price
        self.historical_price = historical_price
        self.volatility = self.calculate_volatility()

    def calculate_volatility(self):
        if not self.historical_price:
            return 0.0
        prices = [price.price for price in self.historical_price]
        returns = np.diff(prices) / prices[:-1]
        volatility = statistics.stdev(returns)
        return volatility

    def calculate_expected_return(self):
        prices = [price.price for price in self.historical_price]
        return sum(prices) / len(prices)
