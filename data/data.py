

from datetime import datetime
from os import path

from pandas import DataFrame
import pandas as pd

from apis.api import BarTypes

bar_fields_config = [
    {
        'name': 'Datetime',
        'type': 'datetime',
        'format': '%y-%m-%d %H:%M:%S'
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
    
    def get_bar_from_file_line(self, bar_line: str) -> dict:
        bar_values = bar_line.split(',')
        bar = {}
        for index, field_config in enumerate(bar_fields_config):
            field_name = field_config['name']
            
            field_type = field_config['type']
            value = bar_values[index]
            if field_type == 'float':
                value = float(value)
            if field_type == 'datetime':
                date_format = field_config['format']
                value = datetime.strptime(value, date_format)

            bar[field_name] = value

        return bar

    def get_bars_from_file_lines(self, symbol_file_path: str) -> DataFrame:
        file_lines = open(symbol_file_path, 'r').readlines()
        bars_data_frame = DataFrame()
        
        for line in file_lines:
            bar = self.get_bar_from_file_line(line)
            bars_data_frame = pd.concat([bar, bars_data_frame.loc[:]]).reset_index(drop=True)
        
        return bars_data_frame

    def read(self, symbol: str, interval: BarTypes, start_datetime: datetime, end_datetime: datetime):
        symbol_file_path = self.is_file_path_exist(symbol, interval)

        if not symbol_file_path:
            return print(f'No data found for {symbol} {interval}')
        
        file_lines = open(symbol_file_path, 'r').readlines()
        return self.get_bars_from_file_lines(file_lines)

    def write(self,):
        pass
    
    def edit(self,):
        pass

    def delete(self,):
        pass


data_manipulator = data('../market_data')