from typing import Literal
import talib
from datetime import datetime, date, time, timedelta
from apis import api, get_bars_dto, DataProvider, BarTypes
from ib_insync import IB
from pandas import DataFrame, Timestamp
from trading_utilities import trading_utilities
from trading_calculations import trading_calculations
from talib_utilities import talib_utilities
from utilities import utilities
from typing import TypedDict
from support_and_resistance import support_and_resistance
from typing import Callable

class SupportAndResistance(TypedDict):
    interval: str
    durationInDays: int

class strategy:

    def __init__(
        self, 
        start_date: date,
        end_date: date,
        start_time: time,
        end_time: time,
        symbols: list[str],
        data_provider: DataProvider=DataProvider.bars_api, 
        ib_app: IB=None, 
        commition: float = 1.8,
        candlestick_patterns: list[str]=[],
        momentum_indicators: list[str]=[],
        volume_indicators: list[str]=[],
        support_and_resistance_config: SupportAndResistance ={},
        interval: BarTypes = BarTypes.one_minute
    ) -> None:
        
        self.ib_app = None
        if data_provider == DataProvider.ib_api:
            assert ib_app is not None, "ib_app must be provider if you choose Interactive to be the data provider"
            self.ib_app = ib_app

        self.start_date = start_date
        self.end_date = end_date

        self.strategy_start_time = start_time
        self.strategy_end_time = end_time

        self.interval = interval
        
        self.data_provider = data_provider

        self.commition = commition
        self.symbols = symbols
        self.candlestick_patterns = candlestick_patterns
        self.momentum_indicators = momentum_indicators
        self.volume_indicators = volume_indicators
        self.support_and_resistance = support_and_resistance_config

        self.market_data: dict[str, DataFrame] = {}
        self.current_bar_idx: str = None
        self.orders: list[dict] = []

    def is_support_and_resistance_selected(self, support_and_resistance: SupportAndResistance):
        return "durationInDays" in support_and_resistance and "interval" in support_and_resistance
    
    def get_snp_data(self, symbol: str, date: date):
        end_date_time = datetime.combine(date, self.strategy_start_time)
        start_date_time = end_date_time - timedelta(days=self.support_and_resistance["durationInDays"])
        params = get_bars_dto(self.data_provider, self.support_and_resistance["interval"], symbol, start_date_time, end_date_time, self.ib_app)
        return api.get_bars(params)
    
    def get_snp_levels(self, symbol: str, date: date):
        support_and_resistance_levels = None
        if self.is_support_and_resistance_selected(self.support_and_resistance):
            snp_data = self.get_snp_data(symbol, date)
            support_and_resistance_levels = support_and_resistance.detect_level_method(snp_data)
        return support_and_resistance_levels
    
    def get_data_with_requirements(self, start_datetime: datetime, end_datetime: datetime, interval: BarTypes, symbol: str):
        market_data = self.get_data(start_datetime, end_datetime, interval, symbol)
        talib_utilities.add_momentum_idicators_to_dataframe(self.momentum_indicators, market_data)
        talib_utilities.add_volume_idicators_to_dataframe(self.volume_indicators, market_data)
        talib_utilities.add_candlestick_patterns_to_dataframe(self.candlestick_patterns, market_data)
        return market_data

    def start(self):
        for date in utilities.daterange(self.start_date, self.end_date):
            if not trading_utilities.is_trading_day(date):
                print(f"Market is close on {date}")
                continue

            self.before_run_logic(date, self.get_snp_levels)
            self.market_data = {}
            start_datetime = datetime.combine(date, self.strategy_start_time)
            end_datetime = datetime.combine(date, self.strategy_end_time)
            for symbol in self.symbols:
                self.market_data[symbol] = self.get_data_with_requirements(start_datetime, end_datetime, self.interval, symbol)
                self.run_logic(symbol, self.market_data)

        self.after_run_logic(self.orders)
    
    def before_run_logic(self, date: date, get_snp_levels: Callable[[str, date], (list[tuple[Timestamp, float]] or None)]):
        # NEED THE INHERIT CLASS TO DEFINE THIS FUNCTION LOGIC 
        pass

    def run_logic(self, symbol: str, market_data: dict[str, DataFrame]):
        # NEED THE INHERIT CLASS TO DEFINE THIS FUNCTION LOGIC 
        pass
    
    def after_run_logic(self, orders: list[dict]):
        # NEED THE INHERIT CLASS TO DEFINE THIS FUNCTION LOGIC 
        pass

    def execute_order(self, symbol: str, action: Literal['BUY', 'SELL'], buy_point: float, take_profit: float, quantity: int, current_bar_idx, stop_loss: float=None, extra_fields: dict={}, cancel_order_after: int=0):
        order = {
            "symbol": symbol,
            "datetime": current_bar_idx,
            "action": action,
            "buy_point": buy_point,
            "take_point": take_profit,
            "stop_loss": stop_loss,
            'quantiy': quantity
        }
        order = utilities.merge_two_dicts(order, extra_fields)
        last_marketdata_index = self.market_data[symbol].index[-1]
        marketdata_from_index_to_end = self.market_data[symbol][current_bar_idx:]

        if cancel_order_after:
            cancel_index = marketdata_from_index_to_end.index[:cancel_order_after][-1]
            marketdata_from_index_to_cancel_index = marketdata_from_index_to_end[:cancel_index]
            buy_point_bar = None
            for index, bar in marketdata_from_index_to_cancel_index.iterrows():
                if buy_point_bar is not None:
                    continue
                buy_point_bar = trading_utilities.is_bar_reach_to_buy_point(action, bar, buy_point)

            if buy_point_bar is not None:
                order['bp_filled_at'] = index
            else:
                order['bp_filled_at'] = 'N/A'
                order["exit_at_price"] = 'N/A'
                order["exit_at_time"] = 'N/A'
                order['pl'] = 'C'
                order["pl_amount"] = 'N/A'
                self.orders.append(order)
                return

        for index, bar in marketdata_from_index_to_end.iterrows():
            pl = trading_utilities.check_pl(action, bar, take_profit, stop_loss)
            if pl:
                order["exit_at_price"] = take_profit if pl == "P" else stop_loss
                order["exit_at_time"] = index
                order['pl'] = pl
                order["pl_amount"] = trading_calculations.pl(order["buy_point"], quantity, take_profit, action, self.commition)
                break
            
            if index == last_marketdata_index:
                order["exit_at_price"] = bar["Close"]
                order["exit_at_time"] = index
                order['pl'] = 'P' if trading_calculations.pl(order["buy_point"], quantity, bar["Close"], action, self.commition) > 0 else 'L'
                order["pl_amount"] = trading_calculations.pl(order["buy_point"], quantity, bar["Close"], action, self.commition)

        self.orders.append(order)
    
    def get_data(self, start_date_time: datetime, end_date_time: datetime, interval: BarTypes, symbol: str) -> DataFrame:
        params = get_bars_dto(self.data_provider, interval, symbol, start_date_time, end_date_time, self.ib_app)
        return api.get_bars(params)

    
    
