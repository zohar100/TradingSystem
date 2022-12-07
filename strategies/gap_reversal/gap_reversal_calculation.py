


from typing import Literal
from trading_calculations import trading_calculations

class gap_reversal_calculation:

    @staticmethod
    def buy_point(dircetion: Literal['BUY', 'SELL'], low: float, high: float):
        if dircetion == 'SELL':
            buy_point = low - 0.01
        elif dircetion == 'BUY':
            buy_point = high + 0.01
        return round(buy_point, 2)
    
    @staticmethod
    def stop_loss(dircetion: Literal['BUY', 'SELL'], high: float, low: float, extra_space: float = 0):
        change = trading_calculations.change(high, low)
        if dircetion == 'SELL':
            stop_loss = high + change
        elif dircetion == 'BUY':
            stop_loss = low - change
        return round(stop_loss, 2) - extra_space
    
    @staticmethod
    def take_profit(dircetion: Literal['BUY', 'SELL'], buy_point: float, stop_loss: float, extra_space: float = 0) -> float:
        if dircetion == 'SELL':
            take_profit = (buy_point - (stop_loss - buy_point)) - extra_space
        elif dircetion == 'BUY':
            take_profit = (buy_point + (buy_point - stop_loss)) + extra_space

        return round(take_profit, 2)
    
    @staticmethod
    def quntity(dircetion: Literal['BUY', 'SELL'], buy_point: float, stop_loss: float, risk: float):
        if dircetion == 'SELL':
            return round(risk / (stop_loss - buy_point))
        elif dircetion == 'BUY':
            return round(risk / (buy_point - stop_loss))