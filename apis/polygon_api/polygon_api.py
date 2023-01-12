from __future__ import annotations
from decouple import config
from .dto.get_bars_dto import get_bars_dto
from .polygon_api_utilities import polygon_api_utilities
from trading_utilities import new_york_timezone
from polygon import RESTClient

API_KEY = config('POLYGON_TOKEN', 'NOT_IMPLEMENTED') 

class polygon_api:
    client = RESTClient(API_KEY)

    @staticmethod
    def get_bars(params: get_bars_dto):
        params.start_date = new_york_timezone.localize(params.start_date)
        params.end_date = new_york_timezone.localize(params.end_date)
        interval_data = params.type.split(' ')
        multiplier = int(interval_data[0])
        timespan = interval_data[1]
        response = polygon_api.client.get_aggs(params.symbol, multiplier, timespan, params.start_date, params.end_date)
        formated_data = polygon_api_utilities.format_bars_resonse(response)

        return formated_data