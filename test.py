from pandas import DataFrame
import pandas as pd
import pytz
from strategy import strategy, DataProvider
from datetime import datetime, date, time, timedelta
from support_and_resistance import support_and_resistance
from talib_utilities.talib_value_label_dicts import candlestick_pattern_label
from strategies import gap_reversal
from ib_insync import IB
from trading_utilities import new_york_timezone
from utilities import utilities

# start_date = date(2021, 12, 1)
# end_date = date(2021, 12, 31)

# gap_reversal_test = gap_reversal(start_date, end_date)

# gap_reversal_test.start()

# from ib_api import ib_api, get_bars_dto
# from ib_insync import IB
from talib_utilities import talib_utilities

# app = IB()
# app.connect(host='127.0.0.1', port=7497, clientId=1)

# start_date = datetime(2023, 1, 2, 9, 31)
# end_date = datetime(2023, 1, 2, 16)
# params = get_bars_dto('1 min', 'AAPL', start_date, end_date, True)
# data = ib_api.get_bars(app, params)

# talib_utilities.add_momentum_idicators_to_dataframe(['RSI'], data)
# talib_utilities.add_volume_idicators_to_dataframe(['VWAP'], data)
# data.to_csv(f'AAPL-INDICATORS.csv', encoding='utf-8')



# import plotly.graph_objects as go
# from ib_api.dto.get_bars_dto import get_bars_dto as get_ib_bars_dto
# from ib_api import ib_api
# from trading_utilities import market_start_time
# from plotly.subplots import make_subplots

# support_and_resistance_config = {
#     "interval": "1 min",
#     "durationInDays": 3
# }

# ib_app = IB()
# ib_app.connect(host='127.0.0.1', port=7497, clientId=1)
# strategy_start_time = market_start_time

# def get_snp_data(symbol: str, date: date):
#     end_date_time = datetime.combine(date, strategy_start_time)
#     start_date_time = end_date_time - timedelta(days=support_and_resistance_config["durationInDays"])
#     params = get_ib_bars_dto(support_and_resistance_config["interval"], symbol, start_date_time, end_date_time, True)
#     data = ib_api.get_bars(ib_app ,params)
#     return data

# symbol = "AAPL"
# market_data = get_snp_data(symbol, date.today())
# print(market_data)
# talib_utilities.add_volume_idicators_to_dataframe(['VWAP'], market_data)
# talib_utilities.add_momentum_idicators_to_dataframe(['RSI'], market_data)

# # Create figure with secondary y-axis
# fig = make_subplots(rows=3, cols=1,
#                     shared_xaxes=True,
#                     vertical_spacing=0.03,
#                     row_width=[0.3, 0.2, 0.7]
#                    )

# fig.add_trace(go.Candlestick(x=market_data.index,
#                             open=market_data['Open'], 
#                             high=market_data['High'],
#                             low=market_data['Low'],
#                             close=market_data['Close']
#                         ), row=1, col=1)
# fig.add_trace(go.Scatter(x=market_data.index, 
#                             y=market_data['VWAP'], 
#                             line=dict(color='orange', width=1),
#                             name='VWAP'
#                         ), row=1, col=1)

# fig.add_trace(go.Bar(x=market_data.index, 
#                     y=market_data['Volume'],
#                     name='Volume'), row=2, col=1)

# fig.add_trace(go.Scatter(x=market_data.index, 
#                         y=market_data['RSI'],
#                         line=dict(color="black"),
#                         name='RSI'), row=3, col=1)
# fig.add_hrect(y0=0, y1=30, 
#                 fillcolor="red",
#                 opacity=0.25,
#                 line_width=0, row=3, col=1)

# fig.add_hrect(y0=70, y1=100,
#                 fillcolor="green", 
#                 opacity=0.25,
#                 line_width=0, row=3, col=1)

# fig.update_yaxes(title_text='Price', row=1, col=1)
# fig.update_yaxes(title_text='Volume', row=2, col=1)
# fig.update_yaxes(title_text='RSI', row=3, col=1)

# fig.update_layout(height=800)

# fig.show()

from polygon_api import polygon_api, get_bars_dto


_from = datetime(2023, 1, 5, 9, 30)
_to = datetime(2023, 1, 5, 16)

params = get_bars_dto('1 minute', 'AAPL', _from, _to)
print(polygon_api.get_bars(params))
