from datetime import datetime
from apis import api
from apis.api import BarTypes, DataProvider, get_bars_dto
from trading_utilities import market_start_time, market_end_time
from talib_utilities import talib_utilities
import pandas as pd

# _from = datetime(2023, 1, 20, 9, 30)
# _to = datetime(2023, 1, 20, 15, 59)

# params = get_bars_dto(DataProvider.poly_api, BarTypes.one_minute, 'AAPL', _from, _to)
# data = api.get_bars(params)

# talib_utilities.add_overlap_studies_to_dataframe(["EMA"], data)

# # for index, row in data.iterrows():
# #     print(index.__str__())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):  
#     print(data)

one, tow, tree = [1, 3, 4]

print(one, tow, tree)