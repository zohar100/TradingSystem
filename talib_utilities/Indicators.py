import pandas_ta as ta
import pandas as pd



# add datafframe argument if not pulling data from any provider in this code
def calculate_all_indicators():
    # List of all indicators in use
    df = pd.DataFrame()
    # Relevant only if pulling data from yFinance 
    df = df.ta.ticker("AAPL",period= '1month',interval = '1m')[['Open','High','Low','Close','Volume']]
    # macd requires at least 26 candles
    df['MACD'] = ta.macd(df.Close, fast=12, slow=26, signal=9, append= True)['MACD_12_26_9']
    df['VWAP'] = calculate_vwap(df)
    df['RSI'] = ta.rsi(df.Close,length=14,fillna= '-')
    df['SMA'] = ta.sma(df.Close,length=14)
    df['EMA'] = ta.ema(df.Close,length=14)
    return df

def calculate_vwap(df):
    df.set_index(pd.DatetimeIndex(df.index), inplace=True)
    df = ta.vwap(df.High,df.Low,df.Close,df.Volume)
    df = df.to_frame()
    return df['VWAP_D']



calculate_all_indicators()