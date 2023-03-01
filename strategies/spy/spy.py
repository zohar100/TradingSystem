import csv
from datetime import date, datetime, time
from itertools import repeat

from typing import Callable

from pandas import DataFrame, Timestamp
from apis import DataProvider, BarTypes
from strategy import strategy
from trading_utilities import market_start_time, market_end_time, pre_market_start_time ,trading_utilities
from talib_utilities import suggested_candlestick_patterns
from trading_calculations import trading_calculations
from support_and_resistance import support_and_resistance

STRATEGY_SYMBOL = "SPY"

class spy(strategy):
    def __init__(self, start_date: date, end_date: date):

        self.risk = 16000

        strategy.__init__(
            self,
            start_date=start_date,
            end_date=end_date,
            symbols=[STRATEGY_SYMBOL],
            start_time=market_start_time,
            end_time=market_end_time,
            data_provider=DataProvider.text_files,
            candlestick_patterns=suggested_candlestick_patterns,
            support_and_resistance_config={
                "interval": "1h",
                "durationInDays": 30
            },
            interval=BarTypes.one_minute
        )
        
        self.last_four_days_data: DataFrame = None
        self.last_trading_date: date = None
        self.last_trading_date_data: DataFrame = None
        self.current_date_snp: list[tuple[Timestamp, float]] = None
        
        self.market_start_datetime = None
        self.market_end_datetime = None

        self.pre_market_data = None

    def check_direction(self, yesterday_close: float, today_open: float, plus: float=0):
        if yesterday_close < today_open - plus:
            return "SELL"
        if yesterday_close > today_open + plus:
            return "BUY"

    def before_run_logic(self, date: date, get_snp_levels: Callable[[str, date], (list[tuple[Timestamp, float]] or None)]):
        super().before_run_logic(date, get_snp_levels)
        
        self.current_date_snp = get_snp_levels(STRATEGY_SYMBOL, date)
        self.market_start_datetime = trading_utilities.attach_market_start_time(date)
        self.market_end_datetime = trading_utilities.attach_market_end_time(date)
        pre_market_start_datetime = trading_utilities.attach_pre_market_start_time(date)
        self.pre_market_data = self.get_data_with_requirements(pre_market_start_datetime, self.market_start_datetime, BarTypes.one_minute, STRATEGY_SYMBOL)

        # Get valid four days back date
        days_go_back = 4
        back_date = date
        for _ in repeat(None, days_go_back):
            back_date = trading_utilities.get_last_trading_date(back_date)
        start_datetime = trading_utilities.attach_market_start_time(back_date)
        end_datetime = trading_utilities.attach_market_end_time(date)
        self.last_four_days_data = self.get_data_with_requirements(start_datetime, end_datetime, BarTypes.one_day, STRATEGY_SYMBOL)
        mask = (trading_utilities.is_trading_day(self.last_four_days_data.index.date))
        self.last_four_days_data = self.last_four_days_data.loc[mask]

        self.last_trading_date = trading_utilities.get_last_trading_date(date)
        start = trading_utilities.attach_market_start_time(self.last_trading_date)
        end = trading_utilities.attach_market_end_time(self.last_trading_date)
        self.last_trading_date_data = self.get_data_with_requirements(start, end, BarTypes.one_minute, STRATEGY_SYMBOL)
    
    def run_logic(self, symbol: str, market_data:  dict[str, DataFrame]):
        super().run_logic(symbol, market_data)
        all_data = market_data[symbol]
        today_data = all_data.loc[self.market_start_datetime:self.market_end_datetime]

        yesterday_close = self.last_trading_date_data["Close"][-1]
        yesterday_high = max(self.last_trading_date_data["High"])
        yesterday_low = min(self.last_trading_date_data["Low"])
        today_open = today_data["Open"][0]

        market_direction = self.check_direction(yesterday_close, today_open)
        if not market_direction:
            print("We dont make a trade today - market_direction")
            return
        
        gap = trading_calculations.gap_percentage(today_open, yesterday_close, market_direction)
        market_size = trading_calculations.market_size_percentage(yesterday_high, yesterday_low)

        is_gap_valid = gap <= 3
        if not is_gap_valid:
            print("We dont make a trade today - gap_valid")
            return

        is_market_size_gap = gap < (market_size * 0.85) and gap > (market_size * 0.15)
        if not is_market_size_gap:
            print("We dont make a trade today - market_size_gap")
            return
        
        print(f"We going to make a {market_direction} trade")

        last_trading_five_min_time = time(15, 55)
        last_trading_five_min_start = datetime.combine(self.last_trading_date, last_trading_five_min_time)
        last_trading_end_date_time = trading_utilities.attach_market_end_time(self.last_trading_date)
        last_trading_day_data_last_five_min = self.last_trading_date_data.loc[last_trading_five_min_start:last_trading_end_date_time]
        # Everything fine we are about to make order
        if market_direction == 'BUY':
            take_profit = min(last_trading_day_data_last_five_min["Low"])
        elif market_direction == 'SELL':
            take_profit = max(last_trading_day_data_last_five_min["High"])
        
        quantity = round(self.risk / today_open)
        last_day_patterns = []
        for pattern in self.candlestick_patterns:
            if self.last_four_days_data[pattern][-1] == market_direction:
                last_day_patterns.append(pattern)
        
        order_extra_fields = {
            "last_day_patterns": ','.join(last_day_patterns),
            "support": support_and_resistance.find_closest_support_point(market_direction, today_open, self.current_date_snp),
            "resistance": support_and_resistance.find_closest_support_point("SELL" if market_direction == "BUY" else "BUY", today_open, self.current_date_snp),
        }
        self.execute_order(STRATEGY_SYMBOL, market_direction, today_open, take_profit, quantity, 0, None, order_extra_fields)

    def after_run_logic(self, orders: list[dict]):
        super().after_run_logic(orders)
        if len(orders) <= 0:
            return
        print(f"Saving {len(self.orders)} orders....")
        keys = self.orders[0].keys()
        with open(f'orders-test.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.orders)
        print("Orders saved")

