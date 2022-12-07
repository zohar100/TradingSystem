


from ib_insync import IB
from pandas import DataFrame
from strategy import DataProvider
from datetime import date, datetime
from trading_utilities import trading_utilities, pre_market_start_time, market_end_time, market_start_time
from .gap_reversal_models import ChosenStock
from ib_api import ib_api, BarType as IbBarTypes, get_bars_dto as get_ib_bars_dto
from bars_api import bars_api, BarType as HttpBarTypes, get_bars_dto as get_http_bars_dto
from .gap_reversal_models import db

class gap_reversal_filter_stocks:
    def __init__(self, symbols_list: list[str], date: date, data_provider: DataProvider, ib_app: IB):

        # assert len(symbols_list) > 0, "Symbols list is empty"
        assert date is not None, "Date most be set"

        if data_provider == DataProvider.IB_API:
            assert ib_app is not None, "If IB is the provider app is required" 
        
        db.connect()
        db.drop_tables([ChosenStock])
        db.create_tables([ChosenStock])

        self.data_provider = data_provider
        
        self.ib_app = ib_app

        self.symbols_list = symbols_list
        self.date = date

        self.last_trading_date = trading_utilities.get_last_trading_date(self.date)

        self.chosen_stocks: list[ChosenStock] = []

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
            try:
                last_trading_day_bars = self.get_all_last_trading_day_bars(symbol)
                bars_from_market_open_time = self.get_bars_from_market_open_time(symbol)
            except Exception as e:
                continue

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
        
        if self.data_provider == DataProvider.BARS_API:
            bar_params = get_http_bars_dto(HttpBarTypes.ONE, [symbol], start_date_time, end_date_time)
            bars = bars_api.get_bars(bar_params)
            return bars
        else:
            bar_params = get_ib_bars_dto(IbBarTypes.ONE, symbol, start_date_time, end_date_time)
            bars = ib_api.get_bars(self.ib_app, bar_params)
            return bars
    
    def get_bars_from_market_open_time(self, symbol: str) -> DataFrame:
        start_date_time = datetime.combine(self.date, pre_market_start_time)
        end_date_time = datetime.combine(self.date, market_start_time)
        
        if self.data_provider == DataProvider.BARS_API:
            bar_params = get_http_bars_dto(HttpBarTypes.ONE, [symbol], start_date_time, end_date_time)
            bars = bars_api.get_bars(bar_params)
            return bars
        else:
            bar_params = get_ib_bars_dto(IbBarTypes.ONE, symbol, start_date_time, end_date_time)
            bars = ib_api.get_bars(self.ib_app, bar_params)
            return bars  
    
    def check_for_chosen_stock(self, symbol: str, last_trading_day_bars: DataFrame, bars_from_market_open_time: DataFrame) -> ChosenStock or None:
        print(symbol)
        print(last_trading_day_bars)
        print(bars_from_market_open_time)
    