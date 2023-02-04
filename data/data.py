

from datetime import datetime
from os import path

from pandas import DataFrame

from apis.api import BarTypes

bar_fields_config = [
    {
        'field_name': 'Datetime',
        'field_type': 'datetime',
    },
    {
        'field_name': 'Open',
        'field_type': 'float'
    },
    {
        'field_name': 'High',
        'field_type': 'float'
    },
    {
        'field_name': 'Low',
        'field_type': 'float'
    },
    {
        'field_name': 'Close',
        'field_type': 'float'
    },
    {
        'field_name': 'Volume',
        'field_type': 'float'
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
    
    def get_bar_from_file_line(bar_line: str) -> dict:
        bar_fields = bar_line.split(',')
        for field, index in bar_fields_config:
            pass
        pass

    def get_bars_from_file(symbol_file_path: str) -> DataFrame:
        file_lines = open(symbol_file_path, 'r').readlines()
        bars_data_frame = DataFrame()
        
        for line in file_lines:
            pass
        
        return

    def read(self, symbol: str, interval: BarTypes, start_datetime: datetime, end_datetime: datetime):
        symbol_file_path = self.is_file_path_exist(symbol, interval)

        if not symbol_file_path:
            return print(f'No data found for {symbol} {interval}')
        
        file_lines = open(symbol_file_path, 'r').readlines()
        print(file_lines[0])

    def write(self,):
        pass
    
    def edit(self,):
        pass

    def delete(self,):
        pass


data_manipulator = data('../market_data')