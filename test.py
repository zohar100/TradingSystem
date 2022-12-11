from strategy import strategy, DataProvider
from datetime import datetime, date, time
from talib_utilities.talib_value_label_dicts import candlestick_pattern_label
from strategies import gap_reversal

start_date = date(2021, 1, 1)
end_date = date(2021, 1, 31)

gap_reversal_test = gap_reversal(start_date, end_date)

gap_reversal_test.start()