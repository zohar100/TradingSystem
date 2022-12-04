from strategy import strategy, DataProvider
from datetime import datetime, date, time
from talib_utilities.talib_value_label_dicts import candlestick_pattern_label

start_date = date(2021, 11, 22)
start_time = time(9, 30)
end_time = time(10, 30)

candlestick_patterns = list(candlestick_pattern_label.keys())[:2]
new_strategy = strategy(
    start_date=start_date, 
    end_date=start_date,
    start_time=start_time, 
    end_time=end_time, 
    symbols=["AAPL"], 
    candlestick_patterns=candlestick_patterns, 
    momentum_indicators=["RSI"], 
    # volume_indicators=["VWAP"]
)

new_strategy.start()
