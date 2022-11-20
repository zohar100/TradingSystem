

class trading_calculations:
    @staticmethod
    def gap_percentage(today_open, yesterday_close):
        return (today_open - yesterday_close) * 100 / today_open

    @staticmethod
    def market_size_percentage(high, low):
        return (high - low) * 100 / high
