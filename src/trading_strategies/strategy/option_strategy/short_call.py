from datetime import datetime

from src.data_access.data_access import DataAccess
from src.data_access.volatility import VolatilityType
from src.trading_strategies.financial_asset.option import Option
from src.trading_strategies.financial_asset.symbol import Symbol
from src.agent.margin_calculator import MarginType
from src.trading_strategies.strategy.option_strategy.calculators.option_pricing import implied_date
from src.trading_strategies.strategy.option_strategy.option_strategy import OptionStrategy
from src.trading_strategies.strategy.option_strategy.calculators.option_strike import calculate_strike, \
    roll_up_strike, get_strike_gap
from src.trading_strategies.strategy.strategy_id import StrategyId
from src.agent.transactions.position import Position
from src.util.expiry_date import closest_expiration_date, nyse_calendar, next_expiry_date


class ShortCall(OptionStrategy):

    def __init__(self, strategy_id: StrategyId, symbol: Symbol, is_itm: bool,
                 is_weekly: bool, weekday, num_of_strikes, scale=1, cross_over=True, same_expiration=True,
                 is_itm2=True, is_weekly2=True, num_of_strikes2=1, parent=None):
        super().__init__(strategy_id, symbol, is_itm, is_weekly,
                         weekday, num_of_strikes, scale)
        self._position = Position.SHORT
        self._parent = parent
        self.asset_name = "short_call"
        self.margin_type = MarginType.SHORT_CALL

    def roll_over(self, stock_price: float, date: datetime, prev_option=None) -> (float, datetime):
        strike_price = calculate_strike(stock_price, self._is_itm, self._num_of_strikes, False)
        expiration_date = next_expiry_date(date, is_weekly=self._is_weekly, weekday=self._weekday)
        return strike_price, expiration_date

    def roll_up(self, stock_price: float, date: datetime, prev_option: Option) -> (float, datetime):
        prev_strike = prev_option.get_strike().price()
        symbol = prev_option.symbol()
        # strike
        strike_price = roll_up_strike(stock_price, prev_strike, self._num_of_strikes)
        # expiration
        premium = prev_option.itm_amount(stock_price) + get_strike_gap(stock_price)
        sigma = DataAccess().get_volaitlity(symbol, VolatilityType.GARCH, date).value
        risk_free_rate = DataAccess().get_risk_free(date).value
        new_expiration = implied_date(stock_price, date, strike_price, risk_free_rate, premium,
                                      sigma, False)
        new_expiration = closest_expiration_date(new_expiration, nyse_calendar)
        return strike_price, new_expiration

    def roll_down(self, stock_price: float, date: datetime, prev_option: Option) -> (float, datetime):
        return self.roll_over(stock_price, date, prev_option)
