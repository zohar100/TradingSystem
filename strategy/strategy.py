from typing import Literal
import talib
from bars_api import get_bars_dto, bars_api
from datetime import datetime, date, time
from enum import Enum
from ib_insync import IB
import yfinance
from pandas import DataFrame
from trading_utilities import trading_utilities
from trading_calculations import trading_calculations

class DataProvider(str, Enum):
    IB_API='ib_api',
    YF_API='yf_api',
    BARS_API='bars_api'

class strategy:

    def __init__(
        self, 
        start_date: date,
        end_date: date,
        start_time: time,
        end_time: time,
        symbols: list[str],
        data_provider: DataProvider=DataProvider.BARS_API, 
        ib_app: IB=None, 
        candlestick_patterns: list[str]=[],
        commition: float = 1.8
    ) -> None:
        if data_provider == DataProvider.IB_API:
            assert ib_app is not None, "ib_app must be provider if you choose Interactive to be the data provider"
            self.ib_app = ib_app
        
        self.data_provider = data_provider

        self.commition = commition
        self.symbols = symbols
        self.candlestick_patterns = candlestick_patterns

        self.market_data = None
        self.current_bar_idx = None
        self.orders = []

    def start(self):
<<<<<<< Updated upstream
        market_data = self.get_data(self.start_datetime, self.end_datetime, self.symbol)
        self.add_candlestick_patterns_marketdata(self.candlestick_patterns, market_data)
        self.market_data = market_data
        print(market_data)
        # for index, bar in market_data.iterrows():
        #     self.current_bar_idx = index
        #     self.execute_order(10, 10, 10)
=======
        for date in utilities.daterange(self.start_date, self.end_date):
            if not trading_utilities.is_trading_day(date):
                print(f"Market is close on {date}")
                continue
            self.before_run_logic(date)
            self.market_data = {}
            start_datetime = datetime.combine(date, self.strategy_start_time)
            end_datetime = datetime.combine(date, self.strategy_end_time)
            for symbol in self.symbols:
                market_data = self.get_data(start_datetime, end_datetime, symbol)
                talib_utilities.add_momentum_idicators_to_dataframe(self.momentum_indicators, market_data)
                talib_utilities.add_volume_idicators_to_dataframe(self.volume_indicators, market_data)
                talib_utilities.add_candlestick_patterns_to_dataframe(self.candlestick_patterns, market_data)
                self.market_data[symbol] = market_data
                self.run_logic(symbol, market_data)
    
    def before_run_logic(self, date: date):
        # NEED THE INHERIT CLASS TO DEFINE THIS FUNCTION LOGIC 
        pass

    def run_logic(self, symbol: str, market_data: DataFrame):
        # NEED THE INHERIT CLASS TO DEFINE THIS FUNCTION LOGIC 
        pass
>>>>>>> Stashed changes

    def execute_order(self, action: Literal['BUY', 'SELL'], buy_point: float, take_profit: float, quantity: int, stop_loss: float=None):
        order = {
            "datetime": self.current_bar_idx,
            "action": action,
            "buy_point": buy_point,
            "take_point": take_profit,
            "stop_loss": stop_loss
        }
        last_marketdata_index = self.market_data.index[-1]
        marketdata_from_index_to_end = self.market_data[self.current_bar_idx:]
        for index, bar in marketdata_from_index_to_end.iterrows():
            pl = trading_utilities.check_pl(action, bar, take_profit, stop_loss)
            if pl:
                order["exit_at_price"] = take_profit if pl == "P" else stop_loss
                order["exit_at_time"] = index
                order["pl"] = trading_calculations.pl(order["buy_point"], quantity, take_profit, action, self.commition)
                break
            
            if index == last_marketdata_index:
                order["exit_at_price"] = bar["Close"]
                order["exit_at_time"] = index
                order["pl"] = trading_calculations.pl(order["buy_point"], quantity, bar["Close"], action, self.commition)

        self.orders.append(order)
    
    def get_data(self, start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        return getattr(self, f'_strategy__get_data_{self.data_provider}')(start_date_time, end_date_time, symbol)
    
    @staticmethod
    def add_candlestick_patterns_marketdata(candlestick_patterns: list[str], market_data: DataFrame):
        if not len(candlestick_patterns):
            return market_data
        op = market_data['Open']
        hi = market_data['High']
        lo = market_data['Low']
        cl = market_data['Close']
        for candle in candlestick_patterns:
            patterns = getattr(talib, candle)(op, hi, lo, cl)
            for index,p in patterns.items():
                if p > 0:
                    patterns[index] = "BUY"
                elif p < 0:
                    patterns[index] = "SELL"
                else:
                    patterns[index] = 'N/A'
            market_data[candle] = patterns

    @staticmethod
    def __get_data_ib_api(self, start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        pass

    @staticmethod
    def __get_data_yf_api(start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        data = yfinance.download(symbol, start=start_date_time, end=end_date_time, threads= False, interval="1m")
        data.rename(columns={
            'Datetime': 'Date',
        }, inplace=True)
        data.drop(['Adj Close'], axis=1, inplace=True)
        return data

    @staticmethod
    def __get_data_bars_api(start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        params = get_bars_dto("1", [symbol], start_date_time, end_date_time)
        data = bars_api.get_bars(params)
        return data
    
    
