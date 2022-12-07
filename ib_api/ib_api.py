
from ib_insync import IB, Contract
import pandas as pd
from .dto.get_bars_dto import get_bars_dto
from utilities import utilities
from .ib_api_utitilities import ib_api_utilities

class ib_api:

    @staticmethod
    def get_bars(app: IB, params: get_bars_dto):
        contract = Contract(symbol=params.symbol, secType='STK', exchange='SMART', primaryExchange='SMART', currency='USD')
        end_date_time = params.end_datetime.strftime("%Y%m%d %H:%M:%S US/Eastern")

        duration_min = utilities.calc_minutes_diff(params.start_datetime, params.end_datetime)
        duration_str = f"{60*(duration_min-1)} s"
        response = app.reqHistoricalData(contract, endDateTime=end_date_time, durationStr=duration_str, barSizeSetting=params.type, whatToShow='TRADES', useRTH=False)
        formated_data = ib_api_utilities.format_bars_resonse(response)
        return formated_data