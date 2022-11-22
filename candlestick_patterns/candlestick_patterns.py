import pandas as pd
from pandas import DataFrame

from trading_calculations import trading_calculations

class candlestick_patterns:
    @staticmethod
    def hummer(bars: DataFrame):
        current_bar = bars.iloc[-1]
        prev_one_bar = bars.iloc[-2] if len(bars.index) >= 2 else None
        prev_two_bar = bars.iloc[-3] if len(bars.index) >= 3 else None
        current_bar_size = trading_calculations.bar_size(
            current_bar["High"], current_bar["Low"])

        if current_bar["High"] > (current_bar["Close"] * 1.01):
            return False

        if len(bars.index) >= 3:
            if (current_bar["Open"] - current_bar["Low"]) >= (current_bar_size * 0.60) and current_bar["Close"] > current_bar["Open"] and current_bar["High"] <= (current_bar["Close"] * 1.02) and prev_one_bar["Close"] < prev_one_bar["Open"] and prev_two_bar["Close"] < prev_two_bar["Open"]:
                return True
        if len(bars.index) == 2:
            if prev_one_bar["Open"] > prev_one_bar["Close"] and (current_bar["Open"] - current_bar["Low"]) >= (current_bar_size * 0.60) and current_bar["Close"] > current_bar["Open"] and current_bar["High"] <= (current_bar["Close"] * 1.02):
                return True
        else:
            if (current_bar["Open"] - current_bar["Low"]) >= (current_bar_size * 0.60) and current_bar["Close"] > current_bar["Open"] and current_bar["High"] <= (current_bar["Close"] * 1.02):
                return True

        return False

    @staticmethod
    def shooting_star(bars: DataFrame):
        current_bar = bars.iloc[-1]
        prev_one_bar = bars.iloc[-2] if len(bars.index) >= 2 else None
        prev_two_bar = bars.iloc[-3] if len(bars.index) >= 3 else None
        current_bar_size = trading_calculations.bar_size(
            current_bar["High"], current_bar["Low"])

        if current_bar["Low"] < (current_bar["Close"] * 0.99):
            return False
        if len(bars.index) >= 3:
            if (current_bar["High"] - current_bar["Open"]) >= (current_bar_size * 0.60) and current_bar["Close"] < current_bar["Open"] and current_bar["Low"] >= (current_bar["Close"] * 0.98) and prev_one_bar["Close"] >= prev_one_bar["Open"] and prev_two_bar["Close"] >= prev_two_bar["Open"]:
                return True
        if len(bars.index) == 2:
            if prev_one_bar["Close"] > prev_one_bar["Open"] and (current_bar["High"] - current_bar["Open"]) >= (current_bar_size * 0.60) and current_bar["Close"] < current_bar["Open"] and current_bar["Low"] >= (current_bar["Close"] * 0.98):
                return True
        else:
            if (current_bar["High"] - current_bar["Open"]) >= (current_bar_size * 0.60) and current_bar["Close"] < current_bar["Open"] and current_bar["Low"] >= (current_bar["Close"] * 0.98):
                return True

        return False

    @staticmethod
    def okar_buy(bars: DataFrame):
        current_bar = bars.iloc[-1]
        current_bar_size = trading_calculations.bar_size(
            current_bar["High"], current_bar["Low"])
        buy_low_wick = current_bar["Open"] - current_bar["Low"]
        buy_high_wick = current_bar["High"] - current_bar["Close"]
        check_wick = current_bar_size * 0.25
        if buy_low_wick > check_wick or buy_high_wick > check_wick:
            return False

        if len(bars.index) >= 3:
            prev_one_bar = bars.iloc[-2]
            prev_two_bar = bars.iloc[-3]
            if current_bar["Close"] > prev_one_bar["Open"] and current_bar["Open"] < prev_one_bar["Close"] and prev_one_bar["Close"] < prev_one_bar["Open"] and prev_two_bar["Close"] < prev_two_bar["Open"]:
                return True

        return False
    
    @staticmethod
    def okar_sell(bars: DataFrame):
        current_bar = bars.iloc[-1]
        current_bar_size = trading_calculations.bar_size(
            current_bar["High"], current_bar["Low"])

        sell_low_wick = current_bar["Close"] - current_bar["Low"]
        sell_high_wick = current_bar["High"] - current_bar["Open"]
        check_wick = current_bar_size * 0.25
        if sell_low_wick > check_wick or sell_high_wick > check_wick:
            return False

        if len(bars.index) >= 3:
            prev_one_bar = bars.iloc[-2]
            prev_two_bar = bars.iloc[-3]
            if current_bar["Open"] > prev_one_bar["Close"] and current_bar["Close"] < prev_one_bar["Open"] and prev_one_bar["Close"] > prev_one_bar["Open"] and prev_two_bar["Close"] > prev_two_bar["Open"]:
                return True

        return False