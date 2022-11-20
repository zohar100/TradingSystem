

from datetime import date
import datetime


class utilities:
    @staticmethod
    def daterange(start_date: date, end_date: date):
        for n in range(int((end_date - start_date).days)+1):
            yield start_date + datetime.timedelta(n)