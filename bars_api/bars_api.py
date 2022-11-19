from __future__ import annotations
from decouple import config
from bars_api.bars_api_utilities import bars_api_utilities

from bars_api.dto.get_bars_dto import get_bars_dto

import requests

END_POINT = config('BARS_API_ENDPOINT', 'http://localhost:3001/api/') 
class bars_api:

    @staticmethod
    def get_bars(params: get_bars_dto):
        params.start_date = bars_api_utilities.format_date_time(params.start_date)
        params.end_date = bars_api_utilities.format_date_time(params.end_date)
        query_string = bars_api_utilities.get_query_string(params.__dict__())

        url = f'{END_POINT}bars{query_string}'
        response = requests.get(url)
        formated_data = bars_api_utilities.format_bars_resonse(response)

        return formated_data