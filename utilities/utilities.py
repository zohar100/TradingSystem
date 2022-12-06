

from datetime import date
import datetime


class utilities:
    @staticmethod
    def daterange(start_date: date, end_date: date):
        for n in range(int((end_date - start_date).days)+1):
            yield start_date + datetime.timedelta(n)
    
    @staticmethod
    def calc_minutes_diff(start_orders_at: datetime.datetime, stop_orders_at: datetime.datetime) -> int:
        c = stop_orders_at - start_orders_at
        minute_duration = int(c.total_seconds() / 60) + 1
        return minute_duration