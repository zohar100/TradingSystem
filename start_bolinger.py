from strategies import bolinger_bands

from datetime import date

start_date = date(2021, 1, 1)
end_date = date(2021, 12, 31)

spy_test = bolinger_bands(start_date, end_date)

spy_test.start()