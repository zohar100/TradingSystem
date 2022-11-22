

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

    @staticmethod
    def pl(buy_point: float, quantity: float, filled_price: float, direction: str, commition: float = 0):
        money_invested = buy_point * quantity
        money_done = filled_price * quantity
        if direction == "BUY":
            return (money_done - money_invested) - commition
        if direction == "SELL":
            return (money_invested - money_done) - commition
    
    @staticmethod
    def bar_size(high: float, low: float):
        return high - low