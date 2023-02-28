from typing import Literal
from pandas import DataFrame
import pandas as pd
import pandas_market_calendars as mcal
import datetime
from datetime import date, time, datetime as dt

import pytz

new_york_timezone = pytz.timezone("US/Eastern")
pre_market_start_time = time(4)
market_start_time = time(9,30)
market_end_time = time(15, 59)

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
    def attach_market_start_time(date: date):
        return dt.combine(date, market_start_time)

    @staticmethod
    def attach_market_end_time(date: date):
        return dt.combine(date, market_end_time)
    
    @staticmethod
    def attach_pre_market_start_time(date: date):
        return dt.combine(date, pre_market_start_time)
    
    @staticmethod
    def check_pl(action: str, bar: DataFrame, take_profit: float, stop_loss: float = None):
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
    
    @staticmethod
    def is_bar_reach_to_buy_point(action: Literal['BUY', 'SELL'], bar: DataFrame, buy_point: float):
        if action == 'BUY':
            if bar['High'] > buy_point:
                return bar
        elif action == 'SELL':
            if bar['Low'] < buy_point:
                return bar

        return None