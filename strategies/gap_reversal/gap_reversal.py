from datetime import time, date, datetime
from bars_api import bars_api, get_bars_dto
from trading_utilities import market_start_time


class gap_reversal:
    strategy_start_time = market_start_time
    strategy_end_time = time(15, 50)

<<<<<<< Updated upstream
    def __init__(self, start_date: date, end_date: date, candle_size: str):
=======
        self.stocks = {
            "AAPL": "BUY"
        }
        self.candlestick_patterns = list(candlestick_pattern_label.keys())[:10]

        strategy.__init__(
            self,
            start_date=start_date,
            end_date=end_date,
            symbols=list(self.stocks.keys()),
            start_time=strategy_start_time,
            end_time=strategy_end_time,
            candlestick_patterns=self.candlestick_patterns,
            momentum_indicators=["RSI"]
        )
>>>>>>> Stashed changes
        pass

    def before_run_logic(self, date: date):
        super().before_run_logic(date)
        # RUN LOGIC TO FIND CHOSENSTOCKS
    
