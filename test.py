from strategy import strategy, DataProvider
from datetime import datetime, date, time
from talib_utilities.talib_value_label_dicts import candlestick_pattern_label
from strategies import gap_reversal

from ib_api.ib_api import ib_api
from ib_api.dto.get_bars_dto import get_bars_dto
from ib_insync import IB

start_date = date(2021, 11, 22)
start_time = time(9, 30)
end_time = time(10, 30)

# gap_reversal_test = gap_reversal(start_date, start_date)

# gap_reversal_test.start()

app = IB()
app.connect(host='127.0.0.1', port=7497, clientId=1)

params = get_bars_dto('1 min', 'AAPL', datetime.combine(start_date,start_time), datetime.combine(start_date,end_time))
bars = ib_api.get_bars(app, params)
print(bars)