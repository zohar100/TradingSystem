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