from datetime import datetime
import pandas as pd

from requests import Response

class bars_api_utilities:
    @staticmethod
    def get_query_string(dict: dict) -> str:
        query_string = '?'
        for key, value in dict.items():

            if type(value) is not list:
                query_string += f'{key}={value}&'
            else:
                for item in value:
                    query_string += f'{key}[]={item}&'

        return query_string
    
    @staticmethod
    def format_date_time(date_time: datetime) -> str:
        return date_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    @staticmethod
    def format_bars_resonse(response: Response) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(response.json())
        return df
