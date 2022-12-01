from strategy import strategy, DataProvider
from datetime import datetime

stra = strategy(DataProvider.BARS_API)

symbol="AAPL"
start_dt = datetime(2018, 8, 22, 9, 30)
end_dt = datetime(2018, 8, 22, 10, 30)
data = stra.get_data(start_dt, end_dt, symbol)
print(data)