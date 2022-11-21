import pandas as pd
import pandas_market_calendars as mcal
import datetime
from datetime import date


class trading_utilities:
    @staticmethod
    def is_trading_day(date: datetime):
        exchange = mcal.get_calendar("NYSE")
        trading = exchange.schedule(start_date=date, end_date=date)
        is_trading_empty = trading.empty
        if (is_trading_empty):
            return False
        return True

    @staticmethod
    def get_last_trading_date(date: date):
        nyse = mcal.get_calendar("NYSE")
        week_ago = date - datetime.timedelta(days=7)
        schedule = nyse.schedule(start_date=week_ago, end_date=date)
        schedule["Dates"] = pd.to_datetime(schedule["market_open"]).dt.date
        schedule = schedule["Dates"]
        last_trading_date = schedule[-2]
        return last_trading_date
    
    @staticmethod
    def check_pl(action: str, bar: pd.DataFrame, take_profit: float, stop_loss: float = None):
        if action == "BUY":
            if bar["High"] >= take_profit or bar["Close"] >= take_profit:
                return "P"
            elif stop_loss and (bar["Low"] <= stop_loss or bar["Close"] <= stop_loss):
                return "L"
        if action == "SELL":
            if bar["Low"] <= take_profit or bar["Close"] <= take_profit:
                return "P"
            elif stop_loss and (bar["High"] >= stop_loss or bar["Close"] >= stop_loss):
                return "L"

        return None