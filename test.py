from datetime import datetime
from apis import api
from apis.api import BarTypes, DataProvider, get_bars_dto
from trading_utilities import market_start_time, market_end_time

_from = datetime(2023, 1, 20, 9, 30)
_to = datetime(2023, 1, 20, 15, 59)

params = get_bars_dto(DataProvider.poly_api, BarTypes.one_minute, 'AAPL', _from, _to)
data = api.get_bars(params)

# for index, row in data.iterrows():
#     print(index.__str__())
print(len(data['Volume'].values))