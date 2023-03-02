
from datetime import datetime, date
from enum import Enum
from ib_insync import IB
from pandas import DataFrame
import yfinance

from .ib_api import get_bars_dto as ib_get_bars_dto, ib_api
from .polygon_api import get_bars_dto as polygon_get_bars_dto
from .polygon_api.polygon_api import polygon_api
from .bars_api import get_bars_dto as bars_get_bars_dto, bars_api

from .text_files import data_manipulator

from trading_utilities import trading_utilities

class BarTypes(str, Enum):
    one_minute = '1m'
    tow_minutes = '2m'
    five_minutes = '5m'
    thirty_minutes = '30m'
    one_hour = '1h'
    one_day = '1d'

class DataProvider(str, Enum):
    ib_api='ib_api',
    yf_api='yf_api',
    bars_api='bars_api'
    poly_api = 'poly_api'
    text_files = 'text_files'

provider_bar_type_map: dict[DataProvider, dict[BarTypes, str]] = { 
    DataProvider.ib_api: {
        BarTypes.one_minute: '1 min',
        BarTypes.tow_minutes: '2 mins',
        BarTypes.five_minutes: '5 mins',
        BarTypes.thirty_minutes: '30 mins',
        BarTypes.one_hour: '1 hour',
        BarTypes.one_day: '1 day'
    },
    DataProvider.yf_api: {
        BarTypes.one_minute: '1m',
        BarTypes.tow_minutes: '2m',
        BarTypes.five_minutes: '5m',
        BarTypes.thirty_minutes: '30m',
        BarTypes.one_hour: '1h',
        BarTypes.one_day: '1d'
    },
    DataProvider.bars_api: {
        BarTypes.one_minute: '1',
    },
    DataProvider.poly_api: {
        BarTypes.one_minute: '1 minute',
        BarTypes.tow_minutes: '2 minute',
        BarTypes.five_minutes: '5 minute',
        BarTypes.thirty_minutes: '30 minute',
        BarTypes.one_hour: '1 hour',
        BarTypes.one_day: '1 day'
    },
    DataProvider.text_files: {
        BarTypes.one_minute: '1min',
        BarTypes.five_minutes: '5min',
        BarTypes.thirty_minutes: '30min',
        BarTypes.one_hour: '1hour',
        BarTypes.one_day: '1day',
    }
}

cach_memory = {}

class get_bars_dto:
    def __init__(self, provider: DataProvider, type: BarTypes, symbol: str, start_date: datetime, end_date: datetime, ib_app: IB = None):
        if provider == DataProvider.ib_api:
            assert ib_app is not None, "ib_app must be provider if you choose Interactive to be the data provider"
        
        bars_type = provider_bar_type_map[provider]
        assert type in bars_type, f"The selected interval not supported in the {provider} provider"

        self.provider = provider
        self.type = bars_type[type]
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.ib_app = ib_app

    def __dict__(self):
        return {
            "type": self.type,
            "symbols": self.symbol,
            "startDate": self.start_date,
            "endDate": self.end_date
        }


class api:
    @staticmethod
    def get_bars(params: get_bars_dto) -> DataFrame:
        if params.provider == DataProvider.ib_api:
            return getattr(api, f'_get_data_{params.provider}')(params.type, params.start_date, params.end_date, params.symbol, params.ib_app)

        return getattr(api, f'_get_data_{params.provider}')(params.type, params.start_date, params.end_date, params.symbol)

    
    @staticmethod
    def _get_data_ib_api(type: str, start_date_time: datetime, end_date_time: datetime, symbol: str, ib_app: IB):
        params = ib_get_bars_dto(type, symbol, start_date_time, end_date_time)
        data = ib_api.get_bars(ib_app ,params)
        return data

    @staticmethod
    def _get_data_yf_api(type: str, start_date_time: datetime, end_date_time: datetime, symbol: str):
        data: DataFrame = yfinance.download(symbol, start=start_date_time, end=end_date_time, threads= False, interval=type)
        data.index = [i.replace(tzinfo=None) for i in data.index]
        data.rename(columns={
            'Datetime': 'Date',
        }, inplace=True)
        data.drop(['Adj Close'], axis=1, inplace=True)
        return data

    @staticmethod
    def _get_data_bars_api(type: str, start_date_time: datetime, end_date_time: datetime, symbol: str):
        params = bars_get_bars_dto(type, [symbol], start_date_time, end_date_time)
        data = bars_api.get_bars(params)
        return data
    

    @staticmethod
    def _get_data_poly_api(type: str, start_date_time: datetime, end_date_time: datetime, symbol: str):
        params = polygon_get_bars_dto(type, symbol, start_date_time, end_date_time)
        data = polygon_api.get_bars(params)
        return data
    
    @staticmethod
    def _get_data_text_files(type: str, start_date_time: datetime, end_date_time: datetime, symbol: str):

        cach_key = f'{type}|{symbol}'
        is_data_cach = cach_key in cach_memory
        available_intervals = provider_bar_type_map[DataProvider.text_files]
        if type != available_intervals[BarTypes.one_day]:
            all_symbol_data = cach_memory[cach_key].copy() if is_data_cach else data_manipulator.read(symbol, type)
            if not is_data_cach:
                cach_memory[cach_key] = all_symbol_data.copy()
            requested_symbol_data = all_symbol_data.loc[start_date_time:end_date_time]
            return requested_symbol_data
        
        all_symbol_data = cach_memory[cach_key].copy() if is_data_cach else data_manipulator.read(symbol, available_intervals[BarTypes.thirty_minutes])

        if not is_data_cach:
            cach_memory[cach_key] = all_symbol_data.copy()

        start_date_time = trading_utilities.attach_market_start_time(start_date_time.date())
        end_date_time = trading_utilities.attach_market_end_time(end_date_time.date())
        symbol_data_in_range = all_symbol_data.loc[start_date_time:end_date_time]

        uniqe_dates: list[date] = list(set(symbol_data_in_range.index.date.tolist()))
        one_day_bars = []
        for uniqe_date in uniqe_dates:
            start = trading_utilities.attach_market_start_time(uniqe_date)
            end = trading_utilities.attach_market_end_time(uniqe_date)
            date_data = symbol_data_in_range.loc[start:end]
            bar = {
                'Datetime': uniqe_date,
                'Open': date_data['Open'][0],
                'High': max(date_data['High']),
                'Low': min(date_data['Low']),
                'Close': date_data['Close'][-1],
                'Volume': sum(date_data['Volume'])
            }
            one_day_bars.append(bar)
        return DataFrame(one_day_bars).set_index('Datetime').sort_index()
    
