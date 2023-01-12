import pandas as pd

from ib_insync import BarData
from trading_utilities import new_york_timezone


class ib_api_utilities:
    @staticmethod
    def format_bars_resonse(response: list[BarData]) -> pd.DataFrame:
        dict_list = [bar.__dict__ for bar in response]
        for bar in dict_list:
            bar["date"] = bar["date"].astimezone(new_york_timezone).replace(tzinfo=None)
            bar["volume"] = bar["volume"] * 100
        df = pd.DataFrame.from_dict(dict_list)
        if not len(df.columns):
            return df
        df.rename(columns={
            'date': 'Datetime',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)
        df.drop(['average', 'barCount'], axis=1, inplace=True)
        df.set_index('Datetime', inplace=True)
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
        return df