from datetime import date

from strategies.gap_reversal.gap_reversal import gap_reversal


start_date = date(2021, 12, 1)
end_date = date(2021, 12, 31)

gap_reversal_test = gap_reversal(start_date, end_date)

gap_reversal_test.start()