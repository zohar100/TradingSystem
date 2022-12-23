

from datetime import date
import datetime


class utilities:
    @staticmethod
    def daterange(start_date: date, end_date: date):
        for n in range(int((end_date - start_date).days)+1):
            yield start_date + datetime.timedelta(n)
    
    @staticmethod
    def calc_minutes_diff(start: datetime.datetime, end: datetime.datetime) -> int:
        c = end - start
        minute_duration = int(c.total_seconds() / 60) + 1
        return minute_duration
    
    @staticmethod
    def merge_two_dicts(x: dict, y: dict):
        z = x.copy()   # start with keys and values of x
        z.update(y)    # modifies z with keys and values of y
        return z