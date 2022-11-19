import pandas as pd
import pandas_market_calendars as mcal
from datetime import datetime


class trading_utilities:
    def is_trading_day(date: datetime):
        exchange = mcal.get_calendar("NYSE")
        trading = exchange.schedule(start_date=date, end_date=date)
        is_trading_empty = trading.empty
        if (is_trading_empty):
            return False
        return True

    def get_last_trading_date(date: datetime):
        nyse = mcal.get_calendar("NYSE")
        week_ago = date - datetime.timedelta(days=7)
        schedule = nyse.schedule(start_date=week_ago, end_date=date)
        schedule["Dates"] = pd.to_datetime(schedule["market_open"]).dt.date
        schedule = schedule["Dates"]
        last_trading_date = schedule[-2]
        formatted_last_trading_date = last_trading_date.strftime("%Y%m%d")
        return formatted_last_trading_date