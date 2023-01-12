
from ib_insync import IB, Contract
import pandas as pd
from .dto.get_bars_dto import get_bars_dto
from utilities import utilities
from .ib_api_utitilities import ib_api_utilities
from datetime import timedelta

class ib_api:

    @staticmethod
    def get_bars(app: IB, params: get_bars_dto):
        contract = Contract(symbol=params.symbol, secType='STK', exchange='SMART', primaryExchange='SMART', currency='USD')
        params.end_datetime = params.end_datetime + timedelta(minutes=1)
        end_date_time = params.end_datetime.strftime("%Y%m%d %H:%M:%S US/Eastern")

        duration_min = utilities.calc_minutes_diff(params.start_datetime, params.end_datetime)
        duration_sec = 60 * duration_min
        if duration_sec > 86400:
            duration_days = round(duration_min/1440)
            duration_str = f"{int(duration_days)} d"
        else:
            duration_str = f"{duration_sec-60} s"
        response = app.reqHistoricalData(contract, endDateTime=end_date_time, durationStr=duration_str, barSizeSetting=params.type, whatToShow='TRADES', useRTH=params.useRTH)
        formated_data = ib_api_utilities.format_bars_resonse(response)
        return formated_data