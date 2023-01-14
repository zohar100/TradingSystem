import csv
from datetime import time, date
from typing import Callable

from pandas import DataFrame, Timestamp

from trading_utilities import market_start_time
from strategy import strategy
from talib_utilities import talib_utilities
from apis.bars_api.bars_api_utilities import api_symbols_list

from .gap_reversal_filter_stocks import gap_reversal_filter_stocks
from .gap_reversal_models import ChosenStock
from .gap_reversal_calculation import gap_reversal_calculation
from .extended_talib import talib as extended_talib
from ib_insync import IB

strategy_start_time = market_start_time
strategy_end_time = time(15, 50)
class gap_reversal(strategy):

    def __init__(self, start_date: date, end_date: date):

        self.stocks: dict[str, ChosenStock] = {}
        self.candlestick_patterns = [
            "CDLDRAGONFLYDOJI",
            "CDLGRAVESTONEDOJI",
            "CDL3LINESTRIKE",
            "CDLENGULFING",
            "CDLEVENINGSTAR",
            "CDLEVENINGDOJISTAR",
            "CDLMORNINGSTAR",
            "CDLMORNINGDOJISTAR",
            "CDLHAMMER",
            "CDLINVERTEDHAMMER",
            "CDLSHOOTINGSTAR",
            "CDLHANGINGMAN",
            "CDLPIERCING"
        ]
        self.risk = 50

        ib_app = IB()
        ib_app.connect(host='127.0.0.1', port=7497, clientId=1)

        strategy.__init__(
            self,
            start_date=start_date,
            end_date=end_date,
            symbols=[],
            start_time=strategy_start_time,
            end_time=strategy_end_time,
            # data_provider=DataProvider.IB_API,
            ib_app=ib_app,
            custom_talib_instance=extended_talib,
            candlestick_patterns=self.candlestick_patterns,
            momentum_indicators=["RSI"],
            support_and_resistance_config={
                "interval": "1 hour",
                "durationInDays": 30
            }
        )
        pass

    def before_run_logic(self, date: date, get_snp_levels: Callable[[str, date], (list[tuple[Timestamp, float]] or None)]):
        super().before_run_logic(date, get_snp_levels)
        self.stocks = {}
        filter_stock_service = gap_reversal_filter_stocks(api_symbols_list, date, self.data_provider, self.ib_app, get_snp_levels)
        filter_stock_service.get_chosen_stocks()
        for chosen_stock in filter_stock_service.chosen_stocks:
            self.stocks[chosen_stock.symbol] = chosen_stock
        self.symbols = list(self.stocks.keys())
        # RUN LOGIC TO FIND CHOSENSTOCKS
    
    def run_logic(self, symbol: str, market_data: DataFrame):
        super().run_logic(symbol, market_data)
        stock = self.stocks[symbol]
        for datetime ,bar in market_data.iterrows():
            if bar["Volume"] <= 0:
                self.symbols.remove(symbol)
                del self.stocks[symbol]
                break
            
            candle_patterns = []
            for pattern in self.candlestick_patterns:
                is_pattern = bar[pattern] == stock.action
                if is_pattern:
                    candle_patterns.append(pattern)
            
            if not len(candle_patterns):
                continue

            if  bar["Low"] >= float(stock.support):
                order_area = "TOP"
                support_distance = bar["Low"] - stock.support
            elif bar["High"] <= float(stock.support):
                order_area = "BOTTOM"
                support_distance = stock.support - bar["High"]

            support_percentage = (support_distance / float(stock.support)) * 100

            # if  bar["Low"] <= float(stock.resistance):
            #     order_area = "TOP"
            #     resistance_distance = bar["Low"] - stock.resistance
            # elif bar["High"] >= float(stock.resistance):
            #     order_area = "BOTTOM"
            #     resistance_distance = stock.resistance - bar["High"]

            # resistance_percentage = (resistance_distance / float(stock.resistance)) * 100

            print(f"Found {len(candle_patterns)} orders opportunity at {datetime} for {symbol}")
            for candle_pattern in candle_patterns:

                stop_loss_high = bar["High"]
                stop_loss_low = bar["Low"]
                is_morning_star_patterns = candle_pattern in ["CDLMORNINGDOJISTAR", "CDLMORNINGSTAR"]
                is_evening_star_patterns = candle_pattern in ["CDLEVENINGDOJISTAR", "CDLEVENINGSTAR"]
                if is_morning_star_patterns:
                    stop_loss_low = market_data["Low"][:datetime][-2]
                if is_evening_star_patterns:
                    stop_loss_high = market_data["High"][:datetime][-2]

                stop_loss = gap_reversal_calculation.stop_loss(stock.action, stop_loss_high, stop_loss_low)
                buy_point = gap_reversal_calculation.buy_point(stock.action, bar["Low"], bar["High"])
                take_profit = gap_reversal_calculation.take_profit(stock.action, buy_point, stop_loss)
                try:
                    quantity = gap_reversal_calculation.quntity(stock.action, buy_point, stop_loss, self.risk)
                except Exception:
                    continue
                extra_fields = { 
                    "pattern": talib_utilities.get_candlestick_pattern_label(candle_pattern),
                    "risk": self.risk,
                    "cs_volume": stock.pre_market_volume,
                    "support": stock.support,
                    "resistance": stock.resistance,
                    "order_area": order_area,
                    "support_distance": support_distance,
                    "support_percentage": support_percentage
                }
                self.execute_order(symbol, stock.action, buy_point, take_profit, quantity, datetime, stop_loss, extra_fields, 3)
        
    
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

