
from datetime import datetime
from enum import Enum
from ib_insync import IB
from pandas import DataFrame
import yfinance

from .ib_api import get_bars_dto as ib_get_bars_dto, ib_api
from .polygon_api import get_bars_dto as polygon_get_bars_dto
from .polygon_api.polygon_api import polygon_api
from .bars_api import get_bars_dto as bars_get_bars_dto, bars_api

class BarTypes(str, Enum):
    one_minute = '1m'
    five_minutes = '5m'

class DataProvider(str, Enum):
    ib_api='ib_api',
    yf_api='yf_api',
    bars_api='bars_api'
    poly_api = 'poly_api'

provider_bar_type_map: dict[DataProvider, dict[BarTypes, str]] = { 
    DataProvider.ib_api: {
        BarTypes.one_minute: '1 min',
        BarTypes.five_minutes: '5 mins'
    },
    DataProvider.yf_api: {
        BarTypes.one_minute: '1m',
        BarTypes.five_minutes: '5m'
    },
    DataProvider.bars_api: {
        BarTypes.one_minute: '1',
        BarTypes.five_minutes: '5'
    },
    DataProvider.poly_api: {
        BarTypes.one_minute: '1 minute',
        BarTypes.five_minutes: '5 minute'
    }
}


class get_bars_dto:
    def __init__(self, provider: DataProvider, type: BarTypes, symbol: str, start_date: datetime, end_date: datetime, ib_app: IB = None):
        if provider == DataProvider.ib_api:
            assert ib_app is not None, "ib_app must be provider if you choose Interactive to be the data provider"

        self.provider = provider
        self.type = provider_bar_type_map[provider][type]
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
