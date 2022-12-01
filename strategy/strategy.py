from datetime import datetime
from enum import Enum
from ib_insync import IB
from bars_api import get_bars_dto, bars_api
from pandas import DataFrame

class DataProvider(str, Enum):
    IB_API='ib_api',
    YF_API='yf_api',
    BARS_API='bars_api'

class strategy:

    def __init__(self, data_provider: DataProvider, ib_app: IB=None ) -> None:
        if data_provider == DataProvider.IB_API:
            assert ib_app is not None, "ib_app must be provider if you choose Interactive to be the data provider"
            self.ib_app = ib_app

        self.data_provider = data_provider
    
    
    def get_data(self, start_date_time: datetime, end_date_time: datetime, symbol: str):
        return getattr(self, f'_strategy__get_data_{self.data_provider}')(start_date_time, end_date_time, symbol)
    
    @staticmethod
    def __get_data_ib_api(start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        print("get_data_ib_api")
        pass
    
    @staticmethod
    def __get_data_yf_api(start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        print("get_data_yf_api")
        pass

    @staticmethod
    def __get_data_bars_api(start_date_time: datetime, end_date_time: datetime, symbol: str) -> DataFrame:
        params = get_bars_dto("1", [symbol], start_date_time, end_date_time)
        data = bars_api.get_bars(params)
        return data
