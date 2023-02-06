

from datetime import datetime
from itertools import zip_longest
from os import path

from pandas import DataFrame
import pandas as pd

from apis.api import BarTypes
import time

bar_fields_config = [
    {
        'name': 'Datetime',
        'type': 'datetime',
        'format': '%Y-%m-%d %H:%M:%S'
    },
    {
        'name': 'Open',
        'type': 'float'
    },
    {
        'name': 'High',
        'type': 'float'
    },
    {
        'name': 'Low',
        'type': 'float'
    },
    {
        'name': 'Close',
        'type': 'float'
    },
    {
        'name': 'Volume',
        'type': 'float'
    },
]



class data:
    def __init__(self, market_data_path: str):
        dirname = path.dirname(__file__)
        self.market_data_directory = path.join(dirname, market_data_path)
        
        is_directory_exist = path.isdir(self.market_data_directory)
        assert is_directory_exist, 'The specify directory not exist'

    def is_file_path_exist(self, symbol: str, interval: BarTypes) -> None or str:
        file_name = f'{symbol}_{interval}.txt'
        symbol_file_path = path.join(self.market_data_directory, symbol, file_name)
        is_symbol_file_exist = path.isfile(symbol_file_path)

        if is_symbol_file_exist:
            return symbol_file_path

        return None
    
    def get_bars_from_file(self, symbol_file_path: str) -> DataFrame:
        bars_data_frame = pd.read_csv(symbol_file_path, sep=",", header=None)
        bars_data_frame.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
        bars_data_frame.set_index('Datetime', inplace=True)
        bars_data_frame.index = pd.to_datetime(bars_data_frame.index, format="%Y-%m-%d %H:%M:%S")

        return bars_data_frame

    def read(self, symbol: str, interval: BarTypes):
        symbol_file_path = self.is_file_path_exist(symbol, interval)

        if not symbol_file_path:
            return print(f'No data found for {symbol} {interval}')
        
        bars = self.get_bars_from_file(symbol_file_path)

        return bars

    def write(self,):
        pass
    
    def edit(self,):
        pass

    def delete(self,):
        pass


data_manipulator = data('../market_data')