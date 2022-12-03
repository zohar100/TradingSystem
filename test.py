from strategy import strategy, DataProvider
from datetime import datetime, date, time
from talib_utilities.candlestick_pattern_label import candlestick_pattern_label

start_date = date(2021, 11, 22)
start_time = time(9, 30)
end_time = time(10, 30)

candlestick_patterns = list(candlestick_pattern_label.keys())[:10]
print(candlestick_patterns)
new_strategy = strategy(start_date, start_time, end_time, "AAPL", candlestick_patterns=candlestick_patterns)

new_strategy.start()