import talib
from trading_calculations import trading_calculations
from pandas import DataFrame

from candlestick_patterns import candlestick_patterns

# BUY -> SELL and SELL -> BUY
SUPER_CDL3LINESTRIKE = getattr(talib, "CDL3LINESTRIKE")
def NEW_CDL3LINESTRIKE(open: DataFrame, high: DataFrame, low: DataFrame, close: DataFrame):
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
def NEW_CDLGRAVESTONEDOJI(open: DataFrame, high: DataFrame, low: DataFrame, close: DataFrame):
    results = SUPER_CDLGRAVESTONEDOJI(open, high, low, close)
    for i,res in results.items():
        if res != -100:
            results[i] = 0
    return results
talib.CDLGRAVESTONEDOJI = NEW_CDLGRAVESTONEDOJI


# CHECK
SUPER_CDLENGULFING = getattr(talib, "CDLENGULFING")
def NEW_CDLENGULFING(open: DataFrame, high: DataFrame, low: DataFrame, close: DataFrame):
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

def OUR_HUMMER(open: DataFrame, high: DataFrame, low: DataFrame, close: DataFrame):
    results = DataFrame(index=open.index, columns=[''])
    results.iloc[:] = 0
    df = DataFrame.from_dict({ 'Open': open, 'High': high, 'Low': low, 'Close': close })
    for index, row in df.iterrows():
        curr = df.loc[open.index[0]:index]
        pattern = candlestick_patterns.hummer(curr)
        if pattern:
            results.loc[index] = 100
            continue
    return results['']
talib.OUR_HUMMER = OUR_HUMMER

def OUR_OKAR_BUY(open: DataFrame, high: DataFrame, low: DataFrame, close: DataFrame):
    results = DataFrame(index=open.index, columns=[''])
    results.iloc[:] = 0
    df = DataFrame.from_dict({ 'Open': open, 'High': high, 'Low': low, 'Close': close })
    for index, row in df.iterrows():
        curr = df.loc[open.index[0]:index]
        pattern = candlestick_patterns.okar_buy(curr)
        if pattern:
            results.loc[index] = 100
            continue
    return results['']
talib.OUR_OKAR_BUY = OUR_OKAR_BUY

def OUR_OKAR_SELL(open: DataFrame, high: DataFrame, low: DataFrame, close: DataFrame):
    results = DataFrame(index=open.index, columns=[''])
    results.iloc[:] = 0
    df = DataFrame.from_dict({ 'Open': open, 'High': high, 'Low': low, 'Close': close })
    for index, row in df.iterrows():
        curr = df.loc[open.index[0]:index]
        pattern = candlestick_patterns.okar_sell(curr)
        if pattern:
            results.loc[index] = -100
            continue
    return results['']
talib.OUR_OKAR_SELL = OUR_OKAR_SELL

def OUR_SHOOTINGSTAR(open: DataFrame, high: DataFrame, low: DataFrame, close: DataFrame):
    results = DataFrame(index=open.index, columns=[''])
    results.iloc[:] = 0
    df = DataFrame.from_dict({ 'Open': open, 'High': high, 'Low': low, 'Close': close })
    for index, row in df.iterrows():
        curr = df.loc[open.index[0]:index]
        pattern = candlestick_patterns.shooting_star(curr)
        if pattern:
            results.loc[index] = -100
            continue
    return results['']
talib.OUR_SHOOTINGSTAR = OUR_SHOOTINGSTAR