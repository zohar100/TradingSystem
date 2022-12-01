from datetime import time
from trading_utilities import market_start_time

strategy_start_time = market_start_time
strategy_end_time = time(15, 50)

class gap_reversal:
    def __init__(self):
        self.orders = []
        