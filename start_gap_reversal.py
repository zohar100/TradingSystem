from datetime import date

from strategies.gap_reversal.gap_reversal import gap_reversal


start_date = date(2022, 12, 6)
end_date = date(2022, 12, 6)

gap_reversal_test = gap_reversal(start_date, end_date)

gap_reversal_test.start()