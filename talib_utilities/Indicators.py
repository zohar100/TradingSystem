import pandas_ta as ta
import pandas as pd



# add datafframe argument if not pulling data from any provider in this code
def calculate_all_indicators():
    # List of all indicators in use
    df = pd.DataFrame()
    # Relevant only if pulling data from yFinance 
    df = df.ta.ticker("AAPL",period= '1month',interval = '1m')[['Open','High','Low','Close','Volume']]
    # if data is from Database - take only Open High Low Close Volume in order to calculate all indicators

    df['MACD'] = ta.macd(df.Close, fast=12, slow=26, signal=9, append= True,fill_na='-')['MACD_12_26_9']
    df['VWAP'] = calculate_vwap(df)
    df['RSI'] = ta.rsi(df.Close,length=14,fillna= '-')
    print(df)

def calculate_vwap(df):
    df.set_index(pd.DatetimeIndex(df.index), inplace=True)
    df = ta.vwap(df.High,df.Low,df.Close,df.Volume)
    df = df.to_frame()
    return df['VWAP_D']



calculate_all_indicators()