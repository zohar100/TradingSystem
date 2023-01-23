import talib
from trading_calculations import trading_calculations

# BUY -> SELL and SELL -> BUY
SUPER_CDL3LINESTRIKE = getattr(talib, "CDL3LINESTRIKE")
def NEW_CDL3LINESTRIKE(open: float, high: float, low: float, close: float):
    results = SUPER_CDL3LINESTRIKE(open, high, low, close)
    for i,res in results.items():
        if res == 100:
            results[i] = -100
        elif res == -100:
            results[i] = 100
    return results
talib.CDL3LINESTRIKE = NEW_CDL3LINESTRIKE


# ONLY SELL DETECTION
SUPER_CDLGRAVESTONEDOJI = getattr(talib, "CDLGRAVESTONEDOJI")
def NEW_CDLGRAVESTONEDOJI(open: float, high: float, low: float, close: float):
    results = SUPER_CDLGRAVESTONEDOJI(open, high, low, close)
    for i,res in results.items():
        if res != -100:
            results[i] = 0
    return results
talib.CDLGRAVESTONEDOJI = NEW_CDLGRAVESTONEDOJI


# CHECK
SUPER_CDLENGULFING = getattr(talib, "CDLENGULFING")
def NEW_CDLENGULFING(open: float, high: float, low: float, close: float):
    results = SUPER_CDLENGULFING(open, high, low, close)
    for i,res in results.items():
        if res == 0:
            continue
        
        if res == -100:
            bar_size = open[i] - close[i]
            twenty_five_percent_of_bar = bar_size * 0.25
            top_wick = high[i] - open[i]
            buttom_wick = close[i] - low[i]
            
        if res == 100:
            bar_size = close[i] - open[i]
            twenty_five_percent_of_bar = bar_size * 0.25
            top_wick = high[i] - close[i]
            buttom_wick = open[i] - low[i]
        
        is_top_wick_greater_than_twenty_five_percent_of_bar = top_wick > twenty_five_percent_of_bar
        is_buttom_wick_greater_than_twenty_five_percent_of_bar = buttom_wick > twenty_five_percent_of_bar
        if is_top_wick_greater_than_twenty_five_percent_of_bar or is_buttom_wick_greater_than_twenty_five_percent_of_bar:
            results[i] = 0

    return results
talib.CDLENGULFING = NEW_CDLENGULFING
