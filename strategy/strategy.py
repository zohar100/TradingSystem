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
from talib_utilities import talib_utilities
from utilities import utilities

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
        commition: float = 1.8,
        candlestick_patterns: list[str]=[],
        momentum_indicators: list[str]=[],
        volume_indicators: list[str]=[],
    ) -> None:
        if data_provider == DataProvider.IB_API:
            assert ib_app is not None, "ib_app must be provider if you choose Interactive to be the data provider"
            self.ib_app = ib_app

        self.start_date = start_date
        self.end_date = end_date

        self.strategy_start_time = start_time
        self.strategy_end_time = end_time
        
        self.data_provider = data_provider

        self.commition = commition
        self.symbols = symbols
        self.candlestick_patterns = candlestick_patterns
        self.momentum_indicators = momentum_indicators
        self.volume_indicators = volume_indicators

        self.market_data: dict[str, DataFrame] = {}
        self.current_bar_idx: str = None
        self.orders: list[dict] = []

    def start(self):
        for date in utilities.daterange(self.start_date, self.end_date):
            self.market_data = {}
            start_datetime = datetime.combine(date, self.strategy_start_time)
            end_datetime = datetime.combine(date, self.strategy_end_time)
            for symbol in self.symbols:
                market_data = self.get_data(start_datetime, end_datetime, symbol)
                talib_utilities.add_momentum_idicators_to_dataframe(self.momentum_indicators, market_data)
                talib_utilities.add_volume_idicators_to_dataframe(self.volume_indicators, market_data)
                talib_utilities.add_candlestick_patterns_to_dataframe(self.candlestick_patterns, market_data)
                print(market_data)
                self.market_data[symbol] = market_data
            #RUN STRATEGY LOGIC WITH THE COLLECTED DATA

    def execute_order(self, symbol: str, action: Literal['BUY', 'SELL'], buy_point: float, take_profit: float, quantity: int, stop_loss: float=None):
        order = {
            "datetime": self.current_bar_idx,
            "action": action,
            "buy_point": buy_point,
            "take_point": take_profit,
            "stop_loss": stop_loss
        }
        last_marketdata_index = self.market_data[symbol].index[-1]
        marketdata_from_index_to_end = self.market_data[symbol][self.current_bar_idx:]
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
    
    