from strategy import strategy, DataProvider
from datetime import datetime, date, time, timedelta
from support_and_resistance import support_and_resistance
from talib_utilities.talib_value_label_dicts import candlestick_pattern_label
from strategies import gap_reversal
from ib_insync import IB

start_date = date(2021, 12, 1)
end_date = date(2021, 12, 31)

gap_reversal_test = gap_reversal(start_date, end_date)

gap_reversal_test.start()

# from ib_api import ib_api, get_bars_dto
# from ib_insync import IB
# from talib_utilities import talib_utilities

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

# symbol = "NTNX"
# snp_data = get_snp_data(symbol, date.today())
# support_and_resistance_levels = support_and_resistance.detect_level_method(snp_data)

# today_open = snp_data["Open"].values[-1]
# print(f"Today open {today_open}")
# support = support_and_resistance.find_closest_support_point('BUY', today_open, support_and_resistance_levels)
# print(f"support: {support}")
# resistance = support_and_resistance.find_closest_support_point('SELL', support, support_and_resistance_levels)
# print(f"resistance: {resistance}")

# support_and_resistance.plot_support_and_resistance_results(support_and_resistance_levels, snp_data, symbol)