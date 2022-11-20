

class trading_calculations:
    @staticmethod
    def gap_percentage(today_open, yesterday_close, direction: str):
        if direction == "SELL":
            return (today_open - yesterday_close) * 100 / today_open
        if direction == "BUY":
            return (yesterday_close - today_open) * 100 / yesterday_close

    @staticmethod
    def market_size_percentage(high, low):
        return (high - low) * 100 / high
