import datetime
import matplotlib.pyplot as plt
import numpy as np

from src.trading_strategies.financial_asset.option import PutOption
from src.trading_strategies.financial_asset.price import Price
from src.trading_strategies.financial_asset.stock import Stock
from src.trading_strategies.financial_asset.symbol import Symbol
from src.trading_strategies.option_pricing import bsm_pricing, implied_t_put
from src.trading_strategies.strategy.option_strategy.naked_put import NakedPut
from src.trading_strategies.strategy.option_strategy.option_strike import calculate_strike
from src.trading_strategies.strategy.strategy_id import StrategyId
from src.trading_strategies.transactions.position import Position
from src.trading_strategies.transactions.positions import Positions
from src.util.expiry_date import next_expiry_date, closest_expiration_date
from src.util.read_file import read_file, get_historical_values
import pandas as pd


def main():
    file_path = '../src/data/sp500_adj_close_prices.csv'
    aapl_symbol = Symbol('AAPL')
    date = datetime.datetime(2010, 1, 4, 0, 0)
    is_itm = False
    num_strike = 1
    is_weekly = True
    weekday = "FRI"

    stock_data = get_historical_values(aapl_symbol, file_path, date.strftime('%Y-%m-%d'))
    stock_data.set_index('Date', inplace=True)

    price = Price(stock_data.loc[date.strftime('%Y-%m-%d %H:%M:%S')].iloc[-1], date)
    aapl_stock = Stock(aapl_symbol, price)

    expiry_date = next_expiry_date(date, True, True)

    strike_price = Price(calculate_strike(aapl_stock.current_price.price(), False, 1, True), aapl_stock.current_price.time())

    premium = bsm_pricing(aapl_stock, strike_price.price(), expiry_date, [], 0.03, False)
    put_option = PutOption(aapl_symbol, strike_price, expiry_date, premium)

    position = Position.SHORT

    naked_put = NakedPut(StrategyId("1"), aapl_symbol, is_itm, position, is_weekly, weekday,
                         num_strike)


    # marginHandler = EquityMarginHandler()
    # margin = marginHandler.naked_put_margin(csl_stock.current_price.price(), put_option.get_strike().price(),
    #                                         put_option.get_premium().price())
    # # print(margin)
    #
    # imply_t = 365 * implied_t_put(csl_stock.current_price.price(), 5.25, 0.03, 0.3, csl_stock.garch_long_run)
    # print(imply_t)

    profit = []

    for i in range(1000):
        if naked_put.update(aapl_stock, put_option) is not None:
            transaction = naked_put.update(aapl_stock, put_option)
            if put_option.get_expiry() == date:
                profit.append((-transaction.calculate_payoff(aapl_stock.current_price), transaction.get_time()))
                put_option = transaction.get_asset()
                continue
            else:
                profit.append((transaction.calculate_premium(), transaction.get_time()))

        date = closest_expiration_date(aapl_stock.current_price.time() + datetime.timedelta(days=1))
        aapl_stock.set_current_price(Price(stock_data.loc[date.strftime('%Y-%m-%d %H:%M:%S')].iloc[-1], date))


    sum = []

    total = 0
    for data in profit:
        total += data[0]
        sum.append((data[1], total))


    df_sum = pd.DataFrame(sum, columns=['Date', 'Value'])
    print(df_sum)

    x = [d[0].strftime('%Y-%m-%d') for d in sum]  # Convert datetime to string
    y = [d[1] for d in sum]

    prices = stock_data.loc[:date.strftime('%Y-%m-%d %H:%M:%S')]

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(df_sum['Date'], df_sum['Value'], linestyle='-')
    plt.plot(prices.index, prices['AAPL'], linestyle='-')
    plt.title('Value over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True)
    plt.show()

    pass

if __name__ == "__main__":
    main()