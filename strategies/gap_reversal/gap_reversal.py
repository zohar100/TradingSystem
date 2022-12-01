from datetime import time, date, datetime
from bars_api import bars_api, get_bars_dto
from trading_utilities import market_start_time


class gap_reversal:
    strategy_start_time = market_start_time
    strategy_end_time = time(15, 50)

    def __init__(self, start_date: date, end_date: date, candle_size: str):
        pass
    
