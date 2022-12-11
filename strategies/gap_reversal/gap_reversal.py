import csv
from datetime import time, date, datetime

from pandas import DataFrame
from bars_api import bars_api, get_bars_dto
from trading_utilities import market_start_time
from strategy import strategy, DataProvider
from talib_utilities import candlestick_pattern_label
from bars_api.bars_api_utilities import api_symbols_list

from .gap_reversal_filter_stocks import gap_reversal_filter_stocks
from .gap_reversal_models import ChosenStock
from .gap_reversal_calculation import gap_reversal_calculation
from ib_insync import IB
import pandas as pd

strategy_start_time = market_start_time
strategy_end_time = time(15, 50)
class gap_reversal(strategy):

    def __init__(self, start_date: date, end_date: date):

        self.stocks: dict[str, ChosenStock] = {}
        self.candlestick_patterns = list(candlestick_pattern_label.keys())
        self.risk = 50

        # ib_app = IB()
        # ib_app.connect(host='127.0.0.1', port=7497, clientId=1)

        strategy.__init__(
            self,
            start_date=start_date,
            end_date=end_date,
            symbols=[],
            start_time=strategy_start_time,
            end_time=strategy_end_time,
            # data_provider=DataProvider.IB_API,
            # ib_app=ib_app,
            candlestick_patterns=self.candlestick_patterns,
            momentum_indicators=["RSI"]
        )
        pass

    def before_run_logic(self, date: date):
        super().before_run_logic(date)
        filter_stock_service = gap_reversal_filter_stocks([], date, self.data_provider, self.ib_app)
        filter_stock_service.get_chosen_stocks()
        for chosen_stock in filter_stock_service.chosen_stocks:
            self.stocks[chosen_stock.symbol] = chosen_stock
        self.symbols = list(self.stocks.keys())
        # RUN LOGIC TO FIND CHOSENSTOCKS
    
    def run_logic(self, symbol: str, market_data: DataFrame):
        super().run_logic(symbol, market_data)
        stock_direction = self.stocks[symbol].action
        for datetime ,bar in market_data.iterrows():
            if bar["Volume"] <= 0:
                self.symbols.remove(symbol)
                del self.stocks[symbol]
                break
            
            candle_patterns = []
            for pattern in self.candlestick_patterns:
                is_pattern = bar[pattern] == stock_direction
                if is_pattern:
                    candle_patterns.append(pattern)
            
            if not len(candle_patterns):
                continue
            
            print(f"Found {len(candle_patterns)} orders opportunity at {datetime} for {symbol}")
            for candle_pattern in candle_patterns:
                stop_loss = gap_reversal_calculation.stop_loss(stock_direction, bar["High"], bar["Low"])
                buy_point = gap_reversal_calculation.buy_point(stock_direction, bar["Low"], bar["High"])
                take_profit = gap_reversal_calculation.take_profit(stock_direction, buy_point, stop_loss)
                try:
                    quantity = gap_reversal_calculation.quntity(stock_direction, buy_point, stop_loss, self.risk)
                except Exception:
                    continue
                extra_fields = { 
                    "pattern": candlestick_pattern_label[candle_pattern],
                    "risk": self.risk,
                    "cs_volume": self.stocks[symbol].pre_market_volume,
                }
                self.execute_order(symbol, stock_direction, buy_point, take_profit, quantity, datetime, stop_loss, extra_fields, 3)
        
    
    def after_run_logic(self, orders: list[dict]):
        super().after_run_logic(orders)
        print(f"Saving {len(self.orders)} orders....")
        keys = self.orders[0].keys()
        with open(f'orders-test.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.orders)
        self.orders = []
        print("Orders saved")

