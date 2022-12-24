from typing import Literal
import talib
from bars_api import get_bars_dto, bars_api
from datetime import datetime, date, time, timedelta
from enum import Enum
from ib_insync import IB
import yfinance
from pandas import DataFrame, Timestamp
from trading_utilities import trading_utilities
from trading_calculations import trading_calculations
from talib_utilities import talib_utilities
from utilities import utilities
from ib_api import ib_api
from ib_api.dto.get_bars_dto import get_bars_dto as get_ib_bars_dto
from typing import TypedDict
from support_and_resistance import support_and_resistance
import plotly.graph_objects as go
from typing import Callable

class SupportAndResistance(TypedDict):
    interval: str
    durationInDays: int

class DataProvider(str, Enum):
    IB_API='ib_api',
    YF_API='yf_api',
    BARS_API='bars_api'

class strategy:

    def __init__(
        self, 
        start_date: date,
        end_date: date,
        start_time: time,
        end_time: time,
        symbols: list[str],
        data_provider: DataProvider=DataProvider.BARS_API, 
        ib_app: IB=None, 
        commition: float = 1.8,
        custom_talib_instance=talib,
        candlestick_patterns: list[str]=[],
        momentum_indicators: list[str]=[],
        volume_indicators: list[str]=[],
        support_and_resistance_config: SupportAndResistance ={}
    ) -> None:
        
        self.ib_app = None
        if data_provider == DataProvider.IB_API or self.is_support_and_resistance_selected(support_and_resistance_config):
            assert ib_app is not None, "ib_app must be provider if you choose Interactive to be the data provider"
            self.ib_app = ib_app

        self.start_date = start_date
        self.end_date = end_date

        self.strategy_start_time = start_time
        self.strategy_end_time = end_time
        
        self.data_provider = data_provider

        self.custom_talib_instance =custom_talib_instance

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
        params = get_ib_bars_dto(self.support_and_resistance["interval"], symbol, start_date_time, end_date_time, True)
        data = ib_api.get_bars(self.ib_app ,params)
        return data
    
    def get_snp_levels(self, symbol: str, date: date):
        support_and_resistance_levels = None
        if self.is_support_and_resistance_selected(self.support_and_resistance):
            snp_data = self.get_snp_data(symbol, date)
            support_and_resistance_levels = support_and_resistance.detect_level_method(snp_data)
        return support_and_resistance_levels

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
                market_data = self.get_data(start_datetime, end_datetime, symbol)
                talib_utilities.add_momentum_idicators_to_dataframe(self.momentum_indicators, market_data)
                talib_utilities.add_volume_idicators_to_dataframe(self.volume_indicators, market_data)
                talib_utilities.add_candlestick_patterns_to_dataframe(self.candlestick_patterns, market_data, self.custom_talib_instance)
                self.market_data[symbol] = market_data
                self.run_logic(symbol, market_data)

        self.after_run_logic(self.orders)
    
    def before_run_logic(self, date: date, get_snp_levels: Callable[[str, date], (list[tuple[Timestamp, float]] or None)]):
        # NEED THE INHERIT CLASS TO DEFINE THIS FUNCTION LOGIC 
        pass

    def run_logic(self, symbol: str, market_data: DataFrame):
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
    
    def get_data(self, start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        return getattr(self, f'_strategy__get_data_{self.data_provider}')(start_date_time, end_date_time, symbol)

    def __get_data_ib_api(self, start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        params = get_ib_bars_dto("1 min", symbol, start_date_time, end_date_time)
        data = ib_api.get_bars(self.ib_app ,params)
        return data

    @staticmethod
    def __get_data_yf_api(start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        data = yfinance.download(symbol, start=start_date_time, end=end_date_time, threads= False, interval="1m")
        data.rename(columns={
            'Datetime': 'Date',
        }, inplace=True)
        data.drop(['Adj Close'], axis=1, inplace=True)
        return data

    @staticmethod
    def __get_data_bars_api(start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        params = get_bars_dto("1", [symbol], start_date_time, end_date_time)
        data = bars_api.get_bars(params)
        return data
    
    
