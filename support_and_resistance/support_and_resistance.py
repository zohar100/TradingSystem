

from typing import Literal
import numpy as np
from pandas import DataFrame, Timestamp
import plotly.graph_objects as go

class support_and_resistance:
    @staticmethod
    def is_far_from_level(value, levels, df: DataFrame) -> bool:    
        ave =  np.mean(df['High'] - df['Low'])    
        return np.sum([abs(value-level)<ave for _,level in levels])==0
    
    @staticmethod
    def detect_level_method(df: DataFrame) -> list[tuple[Timestamp, float]]:
        levels = []
        max_list = []
        min_list = []
        for i in range(5, len(df)-5):
            high_range = df['High'][i-5:i+4]
            current_max = high_range.max()
            if current_max not in max_list:
                max_list = []
            max_list.append(current_max)
            if len(max_list) == 5 and support_and_resistance.is_far_from_level(current_max, levels, df):
                levels.append((high_range.idxmax(), current_max))
            
            low_range = df['Low'][i-5:i+5]
            current_min = low_range.min()
            if current_min not in min_list:
                min_list = []
            min_list.append(current_min)
            if len(min_list) == 5 and support_and_resistance.is_far_from_level(current_min, levels, df):
                levels.append((low_range.idxmin(), current_min))
        return levels
    
    @staticmethod
    def find_closest_support_point(action: Literal['BUY', 'SELL'], price: int, support_and_resistance_levels: list[tuple[Timestamp, float]]):
        levels_numbers = [s[1] for s in support_and_resistance_levels]
        closest = 0.0
        if action == 'BUY':
            for number in levels_numbers:
                if number < price and (closest == 0 or number > closest):
                    closest = number
        elif action == 'SELL':
            for number in levels_numbers:
                if number > price and (closest == 0 or number < closest):
                    closest = number
        return closest
    
    @staticmethod
    def plot_support_and_resistance_results(support_and_resistance_levels: list[tuple[Timestamp, float]], market_data: DataFrame, symbol: str):
        fig = go.Figure(data=[
        go.Scatter(
            x=[list(snp)[0] for snp in support_and_resistance_levels],
            y= [list(snp)[1] for snp in support_and_resistance_levels],
            mode="markers",
            yaxis="y2",
            marker=dict(
                size=16,
            ),
            name="Support And Resistance" ),
        go.Candlestick(
            x=market_data.index,
            open=market_data["Open"],
            high=market_data["High"],
            low=market_data["Low"],
            close=market_data["Close"],
            yaxis="y2",
            name="Candlestick"),
        ])
        fig.update_xaxes(title_text='Date')
        fig.update_yaxes(title_text='Prices')
        fig.update_layout(xaxis_rangeslider_visible=True, 
            title = f'{symbol} Spot Rate'
        ) # Set Set Range Slider Bar and Title
        fig.show()