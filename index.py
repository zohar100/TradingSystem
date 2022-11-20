import datetime
import yfinance

from utilities import utilities
from trading_utilities import trading_utilities
from trading_calculations import trading_calculations

def check_direction(yesterday_close: float, today_open: float, plus: float):
    if yesterday_close < today_open - plus:
        return "SELL"
    if yesterday_close > today_open + plus:
        return "BUY"
    return None

def check_gap(gap: float, market_size: float, direction: str):
    if direction == "SELL":
        return gap < (market_size * 0.85) and gap > (market_size * 0.15)
    if direction == "BUY":
        return gap > (market_size * 0.85) and gap < (market_size * 0.15)


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

    yesterday_close = last_trading_date_data["Close"][-1]
    yesterday_high = max(last_trading_date_data["High"])
    yesterday_low = min(last_trading_date_data["Low"])
    today_open = today_data["Open"][0]

    market_direction = check_direction(yesterday_close, today_open, 0.20)
    if not market_direction:
        print("We dont make a trade today - Not enough gap")
        continue
    
    gap = trading_calculations.gap_percentage(today_open, yesterday_close)
    market_size = trading_calculations.market_size_percentage(yesterday_high, yesterday_low)

    is_gap_valid = check_gap(gap, market_size, market_direction)
    if not is_gap_valid:
        print("We dont make a trade today - Gap not valid")
        continue

    print(f"We going to make a {market_direction} trade")

    # Everything fine we are about to make order
    take_profit = last_trading_date_data["Low"][-1] if market_direction == "BUY" else last_trading_date_data["High"][-1]
    print(f"That is our take profirt {take_profit}")

