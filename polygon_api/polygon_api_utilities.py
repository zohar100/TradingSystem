

from datetime import datetime

from pandas import DataFrame
import pandas as pd
from trading_utilities import new_york_timezone
import pytz

utc = pytz.utc

class polygon_api_utilities:
    @staticmethod
    def format_bars_resonse(response: list) -> DataFrame:
        dict_list = [bar.__dict__ for bar in response]
        for bar in dict_list:
            bar["timestamp"] = datetime.utcfromtimestamp(bar["timestamp"] / 1000).replace(tzinfo=utc).astimezone(new_york_timezone)
            bar["volume"] = bar["volume"] * 100
        df = pd.DataFrame.from_dict(dict_list)
        if not len(df.columns):
            return df
        df.rename(columns={
            'timestamp': 'Datetime',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)
        df.drop(['vwap', 'transactions', 'otc'], axis=1, inplace=True)
        df.set_index('Datetime', inplace=True)
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
        return df