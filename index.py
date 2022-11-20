from datetime import *
import yfinance

from utilities import utilities
from trading_utilities import trading_utilities
from trading_calculations import trading_calculations

market_start_time = time(9,30)
market_end_time = time(16)

def check_direction(yesterday_close: float, today_open: float, plus: float):
    if yesterday_close < today_open - plus:
        return "SELL"
    if yesterday_close > today_open + plus:
        return "BUY"

def check_market_size_gap(gap: float, market_size: float):
    return gap < (market_size * 0.85) and gap > (market_size * 0.15)

def calc_quantity(risk, today_open):
    return round(risk / today_open)

start_date = date(2022, 11, 18)
end_date = date(2022, 11, 18)
dates = utilities.daterange(start_date, end_date)
for today_date in dates:
    spyticker = yfinance.Ticker("SPY")
    last_trading_date = trading_utilities.get_last_trading_date(today_date)

    all_data = spyticker.history(interval="5m", start=last_trading_date, auto_adjust=True, rounding=True)

    last_trading_start_date_time = datetime.combine(last_trading_date, market_start_time)
    last_trading_end_date_time = datetime.combine(last_trading_date, market_end_time)
    last_trading_date_data = all_data.loc[last_trading_start_date_time:last_trading_end_date_time]

    today_start_date_time = datetime.combine(today_date, market_start_time)
    today_end_date_time = datetime.combine(today_date, market_end_time)
    today_data = all_data.loc[today_start_date_time:today_end_date_time]

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
    
    gap = trading_calculations.gap_percentage(today_open, yesterday_close, market_direction)
    market_size = trading_calculations.market_size_percentage(yesterday_high, yesterday_low)

    is_gap_valid = check_market_size_gap(gap, market_size)
    if not is_gap_valid:
        print("We dont make a trade today - Gap not valid")
        continue

    print(f"We going to make a {market_direction} trade")

    # Everything fine we are about to make order
    take_profit = last_trading_date_data["Low"][-1] if market_direction == "BUY" else last_trading_date_data["High"][-1]
    quantity = calc_quantity(8000, today_open)
    print(f"That is our take profirt {take_profit}")
    print(f"That is our quantity {quantity}")

