import talib

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