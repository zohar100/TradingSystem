from strategy import strategy, DataProvider
from datetime import datetime, date, time
from talib_utilities.talib_value_label_dicts import candlestick_pattern_label
from strategies import gap_reversal

from ib_api.ib_api import ib_api
from ib_api.dto.get_bars_dto import get_bars_dto
from ib_insync import IB

start_date = date(2020, 4, 2)
start_time = time(9, 30)
end_time = time(10, 30)

gap_reversal_test = gap_reversal(start_date, start_date)

gap_reversal_test.start()