from apis import api, BarTypes, DataProvider, get_bars_dto
from datetime import datetime, date
from utilities import utilities
from trading_utilities import trading_utilities

from taxonomies import symbol_keywords, symbols

start_date = date(2021, 1, 1)
end_date = date(2021, 12, 31)

for _date in utilities.daterange(start_date, end_date):
    if not trading_utilities.is_trading_day(_date):
        print(f"Market is close on {_date}")
        continue

    last_trading_date = trading_utilities.get_last_trading_date(_date)
    for symbol in symbols:

        keywords = symbol_keywords[symbol]
        """
        Should be news headlines from an API 
        from yesterday to today till 9:00
        """
        fundamentals = ['test', 'test', 'test', 'test', 'test']

        start_dt = trading_utilities.attach_market_start_time(_date)
        end_dt = trading_utilities.attach_market_end_time(_date)
        params = get_bars_dto(DataProvider.text_files, BarTypes.one_day, symbol, start_dt, end_dt)
        today_market_data = api.get_bars(params).iloc[0]

        start_dt = trading_utilities.attach_market_start_time(last_trading_date)
        end_dt = trading_utilities.attach_market_end_time(last_trading_date)
        params = get_bars_dto(DataProvider.text_files, BarTypes.one_day, symbol, start_dt, end_dt)
        last_market_data = api.get_bars(params).iloc[0]

        label = 0
        is_stock_increase = today_market_data['Close'] > last_market_data['Close']
        is_stock_decrease = today_market_data['Close'] < last_market_data['Close']
        if is_stock_increase:
            label = 1
        elif is_stock_decrease:
            label = -1