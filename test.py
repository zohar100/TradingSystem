from strategy import strategy, DataProvider
from datetime import datetime, date, time, timedelta
from support_and_resistance.support_and_resistance import support_and_resistance
from talib_utilities.talib_value_label_dicts import candlestick_pattern_label
from strategies import gap_reversal
from ib_insync import IB

start_date = date(2021, 2, 1)
end_date = date(2021, 2, 28)

gap_reversal_test = gap_reversal(start_date, end_date)

gap_reversal_test.start()


# import plotly.graph_objects as go
# from ib_api.dto.get_bars_dto import get_bars_dto as get_ib_bars_dto
# from ib_api import ib_api
# from trading_utilities import market_start_time

# support_and_resistance_config = {
#     "interval": "1 hour",
#     "durationInDays": 30
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


# symbols = ["AAPL", "TSLA", "MSFT", "GOOG", "NVDA", "AMD", "META", "KO", "BABA", "DIS", "PDD", "FUTU", "BILI", "CRM", "NIO", "SEDG", "SHOP", "DE"]

# snp_data = get_snp_data("AAPL", date.today())
# support_and_resistance_levels = support_and_resistance.detect_level_method(snp_data)
# fig = go.Figure(data=[
#     go.Scatter(
#         x=[list(snp)[0] for snp in support_and_resistance_levels],
#         y= [list(snp)[1] for snp in support_and_resistance_levels],
#         mode="markers",
#         yaxis="y2",
#         marker=dict(
#             size=16,
#         ),
#         name="Support And Resistance"
#     ),
#     go.Candlestick(
#         x=snp_data.index,
#         open=snp_data["Open"],
#         high=snp_data["High"],
#         low=snp_data["Low"],
#         close=snp_data["Close"],
#         yaxis="y2",
#         name="Candlestick"
#     ),
# ])
# # fig.update_xaxes(title_text='Date')
# # fig.update_yaxes(title_text='Prices')
# fig.update_layout(xaxis_rangeslider_visible=True, 
#     title = f'{"AAPL"} Spot Rate'
# ) # Set Set Range Slider Bar and Title
# fig.show()