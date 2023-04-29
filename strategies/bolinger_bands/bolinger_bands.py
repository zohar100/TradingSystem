import csv
from datetime import date, datetime, timedelta

from typing import Callable

from pandas import DataFrame, Timestamp, Timedelta
from apis import DataProvider, BarTypes
from strategy import strategy
from trading_utilities import market_start_time, market_end_time, trading_utilities

STRATEGY_SYMBOLS = ["TSLA"]

class bolinger_bands(strategy):
    def __init__(self, start_date: date, end_date: date):

        self.loan = 20000

        strategy.__init__(
            self,
            start_date=start_date,
            end_date=end_date,
            symbols=STRATEGY_SYMBOLS,
            start_time=market_start_time,
            end_time=market_end_time,
            extra_days_back=1,
            data_provider=DataProvider.text_files,
            interval=BarTypes.five_minutes,
            momentum_indicators=["BBANDS","RSI"]
        )

    def before_run_logic(self, date: date, get_snp_levels: Callable[[str, date], (list[tuple[Timestamp, float]] or None)]):
        super().before_run_logic(date, get_snp_levels)
        pass
    
    def run_logic(self, symbol: str, market_data:  dict[str, DataFrame]):
        super().run_logic(symbol, market_data)
        symbol_data = market_data[symbol]

        today_market_start_dt = trading_utilities.attach_market_start_time(self.current_date)
        today_market_end_dt = trading_utilities.attach_market_end_time(self.current_date)

        last_trading_date = trading_utilities.get_last_trading_date(self.current_date, self.extra_days_back)
        yesterday_market_start_dt = trading_utilities.attach_market_start_time(last_trading_date)
        yesterday_market_end_dt = trading_utilities.attach_market_end_time(last_trading_date)

        today_data = symbol_data.loc[today_market_start_dt:today_market_end_dt]
        yesterday_data = symbol_data.loc[yesterday_market_start_dt:yesterday_market_end_dt]
        if yesterday_data.empty:
            return
        today_open = today_data.loc[today_market_start_dt.strftime('%Y-%m-%d %H:%M:%S')]['Open']
        try:
            yesterday_close = yesterday_data.loc[(yesterday_market_end_dt - timedelta(minutes=4)).strftime('%Y-%m-%d %H:%M:%S')]['Close']
        except Exception:
            print("ERROR: cannot get last trading date close price data")
            print(yesterday_data)
            return

        is_buy_gap = today_open >= (yesterday_close * 1.03)

        if not is_buy_gap:
            return
        
        action = "BUY"

        for dt, bar in today_data.iterrows():
            prev_bar = None
            try:
                prev_bar = today_data.loc[str(dt - Timedelta(minutes=5))]
            except Exception as e:
                continue

            rsi = bar['RSI']
            bolinger_bottom, bolinger_middle, bolinger_top = [bar['upperband'], bar['middleband'], bar['lowerband']]
            close, open, low, high = [bar['Close'], bar['Open'], bar['Low'], bar['High']]
            prev_close, prev_open, prev_low, prev_high = [prev_bar['Close'], prev_bar['Open'], prev_bar['Low'], prev_bar['High']]
            
            if close > bolinger_bottom or high > bolinger_bottom:
                continue
        
            if (rsi > 26 or rsi < 21.5):
                continue

            if low > prev_low + 0.02:
                continue

            buy_point = close + 0.02
            take_profit = bolinger_middle
            quantity = 50

            print(f'*EXECUTE_ORDER*\nDT: {dt}\nBP: {buy_point}\nTP: {take_profit}\nQT: {quantity}')
            self.execute_order(symbol, action, buy_point, take_profit, quantity, dt, None, extra_fields={ 'rsi': rsi })


    def after_run_logic(self, orders: list[dict]):
        super().after_run_logic(orders)
        if len(orders) <= 0:
            return
        profit_orders = []
        for order in orders:
            if order['pl'] == 'P':
                profit_orders.append('P')
        print("*RESULTS*")
        print(f"HIT PERCENTAGE: {(100 / len(orders)) * len(profit_orders)}%")
        print(f"PL: {sum([order['pl_amount'] for order in orders])}")
        print(f"Saving {len(self.orders)} orders....")
        keys = self.orders[0].keys()
        with open(f'{"-".join(STRATEGY_SYMBOLS)}-test.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.orders)
        print("Orders saved")

