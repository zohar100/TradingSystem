

from pandas import DataFrame
import talib
import pandas_ta 
from .talib_consts import candlestick_pattern_label
from .extended_talib import talib as extended_talib

class talib_utilities:
    @staticmethod
    def get_candlestick_pattern_label(value: str):
        return candlestick_pattern_label[value]
    
    @staticmethod
    def add_candlestick_patterns_to_dataframe(candlestick_patterns: list[str], market_data: DataFrame):
        if not len(candlestick_patterns):
            return market_data
        open = market_data['Open']
        high = market_data['High']
        low = market_data['Low']
        close = market_data['Close']
        for candle in candlestick_patterns:
            patterns = getattr(extended_talib, candle)(open, high, low, close)
            for index,p in patterns.items():
                if p > 0:
                    patterns[index] = "BUY"
                elif p < 0:
                    patterns[index] = "SELL"
                else:
                    patterns[index] = 'N/A'
            market_data[candle] = patterns
    
    @staticmethod
    def add_momentum_idicators_to_dataframe(indicators: list[str], market_data: DataFrame):
        if not len(indicators):
            return market_data
        close = market_data['Close']
        for indicator in indicators:
            func_to_exec = getattr(talib, indicator)
            if indicator == "RSI":
                market_data[indicator] =  func_to_exec(close, timeperiod=14)
            if indicator == "MACD":
                market_data[indicator] =  func_to_exec(close, fastperiod=12, slowperiod=26, signalperiod=9)



    @staticmethod
    def add_volume_idicators_to_dataframe(indicators: list[str], market_data: DataFrame):
        if not len(indicators):
            return market_data
        close = market_data['Close']
        high = market_data['High']
        low = market_data['Low']
        volume = market_data['Volume']
        for indicator in indicators:
            # func_to_exec = getattr(talib, indicator)
            if indicator == "VWAP":
                market_data[indicator] = pandas_ta.vwap(high,low,close,volume)