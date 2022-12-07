from datetime import time, date, datetime

from pandas import DataFrame
from bars_api import bars_api, get_bars_dto
from trading_utilities import market_start_time
from strategy import strategy
from talib_utilities import candlestick_pattern_label
from .gap_reversal_filter_stocks import gap_reversal_filter_stocks
from bars_api.bars_api_utilities import api_symbols_list

strategy_start_time = market_start_time
strategy_end_time = time(15, 50)
class gap_reversal(strategy):

    def __init__(self, start_date: date, end_date: date):

        self.stocks = {
            "AAPL": "BUY"
        }
        self.candlestick_patterns = list(candlestick_pattern_label.keys())[:10]

        strategy.__init__(
            self,
            start_date=start_date,
            end_date=end_date,
            symbols=list(self.stocks.keys()),
            start_time=strategy_start_time,
            end_time=strategy_end_time,
            candlestick_patterns=self.candlestick_patterns,
            momentum_indicators=["RSI"]
        )
        pass

    def before_run_logic(self, date: date):
        super().before_run_logic(date)
        print("before_run_logic")
        filter_stock_service = gap_reversal_filter_stocks(api_symbols_list[:10], date, self.data_provider, self.ib_app)
        filter_stock_service.get_chosen_stocks()
        # RUN LOGIC TO FIND CHOSENSTOCKS
    
    def run_logic(self, symbol: str, market_data: DataFrame):
        super().run_logic(symbol, market_data)
        # for bar in market_data.iterrows():
        #     print(bar)

