import datetime
import yfinance

from utilities import utilities
from trading_utilities import trading_utilities

start_date = datetime.date(2022, 11, 18)
end_date = datetime.date(2022, 11, 18)
dates = utilities.daterange(start_date, end_date)
for date in dates:
    spyticker = yfinance.Ticker("SPY")

    last_trading_date = trading_utilities.get_last_trading_date(date)
    last_trading_date_data = spyticker.history(period="max", interval="5m", start=last_trading_date, auto_adjust=True, rounding=True)
    today_data = spyticker.history(period="max", interval="5m", start=date, auto_adjust=True, rounding=True)

    print(last_trading_date_data)
    print(today_data)