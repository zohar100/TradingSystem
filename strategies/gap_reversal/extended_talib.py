import talib

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
