import csv
import pandas as pd
import talib
import pytz
from datetime import date, datetime
from ib_insync import *

from trading_utilities import market_end_time, market_start_time

tz_ny = pytz.timezone("US/Eastern")
def format_ib_bar(bar: dict):
    fields = ["Date", "High", "Open", "Low", "Close", "Volume"]
    new_bar = {}
    for field in fields:
        if field == "Date":
            new_bar[field] = bar[field.lower()].astimezone(tz_ny)
        else:
            new_bar[field] = bar[field.lower()]
    return new_bar

def get_data_from_ib(end_date: date, symbol: str):
    date_and_time = datetime.combine(end_date, market_end_time)
    formatted_end_date = date_and_time.strftime("%Y%m%d %H:%M:%S US/Eastern")
    spy_ticker = Contract(symbol=symbol, secType="STK", exchange="SMART", currency="USD")
    
    data = ib.reqHistoricalData(spy_ticker, formatted_end_date, f"1 D", "1 min", "TRADES", True)
    dict_data = [format_ib_bar(bar.__dict__) for bar in data]
    df_data = pd.DataFrame(dict_data).set_index('Date')
    return df_data

ib = IB()
ib.connect(host='127.0.0.1', port=7497, clientId=1)

# col_names = ["Date","High","Open","Low","Close","Volume"]
# data = pd.read_csv('./data/SPY/SPY-2022.csv', skiprows=196909, names=col_names, index_col="Date")
symbol = "AAPL"
end_date = date(2022, 11, 21)
data = get_data_from_ib(end_date, symbol)
# today_start_date_time = datetime.combine(end_date, market_start_time)
# today_end_date_time = datetime.combine(end_date, market_end_time)
# data = data.loc[today_start_date_time:today_end_date_time]
print(data)

pattens = {}

candles_value_label = {
    "CDLMARUBOZU": "Marubozu",
    "CDLDRAGONFLYDOJI": "Dragonfly Doji",
    "CDLGRAVESTONEDOJI": "Gravestone Doji",
    "CDL3LINESTRIKE": "Three-Line Strike",
    "CDLENGULFING": "Engulfing Pattern",
    "CDLEVENINGSTAR": "Evening Star",
    "CDLEVENINGDOJISTAR": "Evening Doji Star",
    "CDLMORNINGSTAR": "Morning Star",
    "CDLMORNINGDOJISTAR": "Morning Doji Star",
    "CDLHAMMER": "Hammer",
    "CDLINVERTEDHAMMER": "Inverted Hammer",
    "CDLSHOOTINGSTAR": "Shooting Star",
    "CDLHANGINGMAN": "Hanging Man",
    "CDLPIERCING": "Piercing Pattern"
}

candle_names = list(candles_value_label.keys())

op = data['Open']
hi = data['High']
lo = data['Low']
cl = data['Close']

for candle in candle_names:
    pattens[candle] = getattr(talib, candle)(op, hi, lo, cl)


patterns_to_save = []
for patten, _data in pattens.items():
    for time, is_pattern in _data.items():
        if is_pattern:
            pattern_to_save = {
                "symbol": symbol,
                "time": time,
                "Close": data.loc[time]["Close"],
                "High": data.loc[time]["High"],
                "Low": data.loc[time]["Low"],
                "Open": data.loc[time]["Open"],
                "Volume": data.loc[time]["Volume"],
                "pattern": candles_value_label[patten],
                "direction": "SELL" if is_pattern < 0 else "BUY"
            }
            patterns_to_save.append(pattern_to_save)

keys = patterns_to_save[0].keys()
with open(f'{symbol}-patterns-21-11-2022.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(patterns_to_save)