from strategies import spy
from datetime import date

start_date = date(2020, 1, 1)
end_date = date(2020, 12, 31)

spy_test = spy(start_date, end_date)

spy_test.start()