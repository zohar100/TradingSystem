import pandas_ta as ta
import pandas as pd


class Indicator:

    def calculate_all_indicators(self,df):
        # List of all indicators in use
        list_of_indicators = ['MACD_12_26_9','MACDh_12_26_9','MACDs_12_26_9','VWAP','RSI','EMA','SMA']
        df = pd.DataFrame()
        # Relevant only if pulling data from yFinance 
        df = df.ta.ticker("AAPL",period= '1month',interval = '1m')[['Open','High','Low','Close','Volume']]
        # if data is from Database - take only Open High Low Close Volume in order to calculate all indicators

        macd_df = self.calculate_macd(df)
        df['MACD_12_26_9'],df['MACDh_12_26_9'],df['MACDs_12_26_9'] = macd_df['MACD_12_26_9'],macd_df['MACDh_12_26_9'],macd_df['MACDs_12_26_9']
        df['VWAP'] = self.calculate_vwap(df)
        df['RSI'] = ta.rsi(df.Close,length=14,fillna= '-')
        df['EMA'] = ta.ema(df.Close,length=14,fillna= '-')
        df['SMA'] = ta.sma(df.Close,length=14,fillna= '-')
        df = df.reset_index()
        results = {}
        
        for indicator in list_of_indicators:
            results[indicator] = float(df[indicator].values[-1:])

        print(results)
        # return dictionary with values of all indicators
        return results

    def calculate_macd(self,df):
        temp_df = ta.macd(df.Close, fast=12, slow=26, signal=9, append= True)
        return temp_df


    def calculate_vwap(self,df):
        df.set_index(pd.DatetimeIndex(df.index), inplace=True)
        df = ta.vwap(df.High,df.Low,df.Close,df.Volume)
        df = df.to_frame()
        return df['VWAP_D']

