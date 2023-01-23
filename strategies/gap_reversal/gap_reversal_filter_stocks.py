


from typing import Callable, Literal
from ib_insync import IB
from pandas import DataFrame, Timestamp
from datetime import date, datetime
from support_and_resistance.support_and_resistance import support_and_resistance
from talib_utilities import talib_utilities, suggested_candlestick_patterns
from trading_utilities import trading_utilities, pre_market_start_time, market_end_time, market_start_time
from .gap_reversal_models import ChosenStock
from apis import api, get_bars_dto, DataProvider
from .gap_reversal_models import db
from trading_calculations import trading_calculations
from itertools import repeat

class gap_reversal_filter_stocks:
    def __init__(self, symbols_list: list[str], date: date, data_provider: DataProvider, ib_app: IB, get_snp_levels: Callable[[str, date], (list[tuple[Timestamp, float]] or None)]):

        # assert len(symbols_list) > 0, "Symbols list is empty"
        assert date is not None, "Date most be set"

        if data_provider == DataProvider.ib_api:
            assert ib_app is not None, "If IB_API is the provider ib_app is required" 
        
        db.connection()
        db.drop_tables([ChosenStock])
        db.create_tables([ChosenStock])

        self.data_provider = data_provider
        
        self.ib_app = ib_app

        self.symbols_list = symbols_list
        self.date = date

        self.last_trading_date = trading_utilities.get_last_trading_date(self.date)

        self.chosen_stocks: list[ChosenStock] = []

        self.get_snp_levels = get_snp_levels

    def get_chosen_stocks(self):

        print("Try to find chosen stocks in the DB...")
        chsoen_stocks: list[ChosenStock] = ChosenStock.select().where(ChosenStock.date == self.date)
        if len(chsoen_stocks) > 0:
            print("Chosen stocks found in the DB")
            for chsoen_stock in chsoen_stocks:
                self.chosen_stocks.append(chsoen_stock)
            return

        print("Chosen stocks not found in the DB")
        for symbol in self.symbols_list:
            print(f"Getting bars for {symbol}")

            last_trading_day_bars = self.get_all_last_trading_day_bars(symbol)
            bars_from_market_open_time = self.get_bars_from_market_open_time(symbol)
            print(bars_from_market_open_time)


            if len(last_trading_day_bars) <= 0 or len(bars_from_market_open_time) <= 0:
                print(f"Error getting bars for {symbol}: Bars not available")
                continue

            print("Check fit...")
            chosen_stock = self.check_for_chosen_stock(symbol, last_trading_day_bars, bars_from_market_open_time)

            if chosen_stock is not None:
                print(f"Chosen stock found: {chosen_stock.symbol}")
                chosen_stock.save()
                self.chosen_stocks.append(chosen_stock)

    def get_all_last_trading_day_bars(self, symbol: str) -> DataFrame:
        start_date_time = datetime.combine(self.last_trading_date, market_start_time)
        end_date_time = datetime.combine(self.last_trading_date, market_end_time)
        params = get_bars_dto(self.data_provider, '1m', symbol, start_date_time, end_date_time, self.ib_app)
        return api.get_bars(params)
    
    def get_bars_from_market_open_time(self, symbol: str) -> DataFrame:
        start_date_time = datetime.combine(self.date, pre_market_start_time)
        end_date_time = datetime.combine(self.date, market_start_time)
        params = get_bars_dto(self.data_provider, '1m', symbol, start_date_time, end_date_time, self.ib_app)
        return api.get_bars(params)
    
    def get_four_days_bars(self, symbol: str) -> DataFrame:
        start_date_time = self.date
        end_date_time = self.date
        # Get valid four days back date
        for i in repeat(None, 4):
            end_date_time = trading_utilities.get_last_trading_date(end_date_time)

        params = get_bars_dto(self.data_provider, '1d', symbol, start_date_time, end_date_time, self.ib_app)
        return api.get_bars(params)

    def get_relevant_support_points(self, action: Literal['BUY', 'SELL'], yesterday_close: int, support_and_resistance_levels: list[tuple[Timestamp, float]]) -> tuple[float, float] or None:
        support = support_and_resistance.find_closest_support_point(action, yesterday_close, support_and_resistance_levels)
        if support == 0:
            return None

        resistance_action = 'BUY' if action == 'SELL' else 'SELL'
        resistance = support_and_resistance.find_closest_support_point(resistance_action, support, support_and_resistance_levels)
        return (support, resistance)
    
    def today_open_is_geater_than_support(self, action: Literal['BUY', 'SELL'], today_open: float, closest_open: float) -> bool:
        if action == 'BUY': 
            if today_open > closest_open:
                return True
        elif action == 'SELL':
            if today_open < closest_open:
                return True
        return False
    
    def check_for_chosen_stock(self, symbol: str, last_trading_day_bars: DataFrame, pre_market_to_open_bars: DataFrame) -> ChosenStock or None:
        last_day_volume = last_trading_day_bars["Volume"].values
        # Check for len because some api dont return bars with volume 0
        is_last_day_had_volume_zero = 0 in last_day_volume or len(last_day_volume) < 390
        if is_last_day_had_volume_zero:
            return None
        
        pre_market_volume = sum(pre_market_to_open_bars["Volume"].values[:-2])
        is_pre_market_volume_under_hundred_thousands = pre_market_volume < 100000
        if is_pre_market_volume_under_hundred_thousands:
            return None

        close_price = pre_market_to_open_bars["Close"].values[-3]
        is_close_price_under_or_equal_ten = close_price <= 10
        if is_close_price_under_or_equal_ten:
            return None
        
        yesterday_close_price = last_trading_day_bars["Close"].values[-1]
        today_open_price = pre_market_to_open_bars["Open"].values[-3]
        is_sell_gap = today_open_price <= (yesterday_close_price * 0.97)
        is_buy_gap = today_open_price >= (yesterday_close_price * 1.03)
        if not is_sell_gap and not is_buy_gap:
            return None

        direction = 'SELL' if is_sell_gap else 'BUY' 
        
        support_and_resistance_levels = self.get_snp_levels(symbol, self.date)
        relevant_support_resistance_points = self.get_relevant_support_points(direction, today_open_price, support_and_resistance_levels)
        if not relevant_support_resistance_points:
            return None

        if not self.today_open_is_geater_than_support(direction, today_open_price, float(relevant_support_resistance_points[0])):
            return None
        
        gap = trading_calculations.gap_percentage(today_open_price, yesterday_close_price, direction)

        last_four_days_bars = self.get_four_days_bars(symbol)
        talib_utilities.add_candlestick_patterns_to_dataframe(suggested_candlestick_patterns, last_day_volume)
        patterns = []
        for candlestick_pattern in suggested_candlestick_patterns:
            if last_four_days_bars[candlestick_pattern].values[-1] != "N/A":
                patterns.append(talib_utilities.get_candlestick_pattern_label(candlestick_pattern))

        return ChosenStock(
            symbol=symbol,
            action=direction,
            yesterday_close=yesterday_close_price, 
            today_open=today_open_price, 
            date=self.date,
            pre_market_volume=pre_market_volume,
            gap=gap,
            support=float(relevant_support_resistance_points[0]),
            resistance=float(relevant_support_resistance_points[1]),
            patterns=', '.join(patterns)
        )