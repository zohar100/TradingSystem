import talib
from bars_api import get_bars_dto, bars_api
from datetime import datetime, date, time
from enum import Enum
from ib_insync import IB, Contract
import yfinance
from pandas import DataFrame

class DataProvider(str, Enum):
    IB_API='ib_api',
    YF_API='yf_api',
    BARS_API='bars_api'

class strategy:

    def __init__(
        self, 
        date: date,
        start_time: time,
        end_time: time,
        symbol: str,
        data_provider: DataProvider=DataProvider.BARS_API, 
        ib_app: IB=None, 
        candlestick_patterns: list[str]=[],
    ) -> None:
        if data_provider == DataProvider.IB_API:
            assert ib_app is not None, "ib_app must be provider if you choose Interactive to be the data provider"
            self.ib_app = ib_app
        
        self.data_provider = data_provider

        self.symbol = symbol
        self.start_datetime = datetime.combine(date, start_time)
        self.end_datetime = datetime.combine(date, end_time)
        self.candlestick_patterns = candlestick_patterns

        self.orders = []

    def start(self):
        market_data = self.get_data(self.start_datetime, self.end_datetime, self.symbol)
        market_data_with_candlestick_patterns = self.add_candlestick_patterns_marketdata(self.candlestick_patterns, market_data)

    def execute_order(self):
        pass
    
    def get_data(self, start_date_time: datetime, end_date_time: datetime, symbol: str):
        return getattr(self, f'_strategy__get_data_{self.data_provider}')(start_date_time, end_date_time, symbol)
    
    @staticmethod
    def add_candlestick_patterns_marketdata(candlestick_patterns: list[str], market_data: DataFrame) -> DataFrame:
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
        return market_data

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
    
    
