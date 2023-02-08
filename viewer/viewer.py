from datetime import datetime
import random
import numpy as np

from pandas import DataFrame
from apis import DataProvider, api, get_bars_dto
from talib_utilities import talib_utilities, suggested_candlestick_patterns as candlestick_patterns, suggested_momentum_indicators, suggested_volume_indicators
import tkinter
import tkcalendar
from ib_insync import IB

data_provider_label = {
    DataProvider.bars_api: 'Our Api',
    DataProvider.yf_api: 'Yahoo Finance',
    DataProvider.poly_api: 'Polygon',
    DataProvider.ib_api: 'Interactive Brokers',
    DataProvider.text_files: 'Text Files'
}

indicators = suggested_volume_indicators + suggested_momentum_indicators

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def plot_candlesticks(market_data: DataFrame, symbol: str, selected_patterns: list[str]):

    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_width=[0.3, 0.3, 0.7]
                    )

    fig.add_trace(go.Candlestick(x=market_data.index,
                                open=market_data['Open'], 
                                high=market_data['High'],
                                low=market_data['Low'],
                                close=market_data['Close'],
                            ), row=1, col=1)
    
    colors = []
    for i in range(len(market_data['Close'])):
        if i != 0:
            if market_data['Close'][i] > market_data['Close'][i-1]:
                colors.append('green')
            else:
                colors.append('red')
        else:
            colors.append('red')
    fig.add_trace(go.Bar(x=market_data.index, 
                        y=market_data['Volume'],
                        name='Volume', marker=dict( color=colors )), row=2, col=1)
    
    if len(selected_patterns) > 0:
        for pattern in selected_patterns:
            d=0.30
            market_data["Marker"] = np.where(market_data["Open"]<market_data["Close"], market_data["High"]+d, market_data["Low"]-d)
            fig.add_trace(
                go.Scatter(marker=dict(size=10),
                            x=market_data.loc[market_data[pattern] != 'N/A'].index, y=market_data.loc[market_data[pattern] != 'N/A']['Marker'],
                            mode='markers', name=talib_utilities.get_candlestick_pattern_label(pattern)
                            ), row = 1, col=1)
    
    if 'VWAP' in market_data.columns:
        fig.add_trace(go.Scatter(x=market_data.index, 
                                y=market_data['VWAP'], 
                                line=dict(color='orange', width=1),
                                name='VWAP'
                            ), row=1, col=1)

    if 'RSI' in market_data.columns:
        fig.add_trace(go.Scatter(x=market_data.index, 
                                y=market_data['RSI'],
                                line=dict(color="black"),
                                name='RSI'), row=3, col=1)
        fig.add_hrect(y0=0, y1=30, 
                        fillcolor="red",
                        opacity=0.25,
                        line_width=0, row=3, col=1)

        fig.add_hrect(y0=70, y1=100,
                        fillcolor="green", 
                        opacity=0.25,
                        line_width=0, row=3, col=1)
        fig.update_yaxes(title_text='RSI', row=3, col=1)

    fig.update_yaxes(title_text='Price', row=1, col=1)
    fig.update_yaxes(title_text='Volume', row=2, col=1)

    fig.update_layout(height=800, title=symbol)

    fig.show()

class Viewer(tkinter.Frame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)

        self.symbol_input_label = tkinter.Label(text="Enter symbol")
        self.symbol_input_label.grid(row = 0, column = 0, pady=20, sticky="W")
        self.symbol_input = tkinter.Entry()
        self.symbol_input.insert(0, 'AAPL')
        self.symbol_input.grid(row = 1, column = 0, sticky="W")

        self.start_date_label = tkinter.Label(text="Enter start date")
        self.start_date_label.grid(row =2, column = 0, pady=20, sticky="W")
        self.start_date_picker = tkcalendar.DateEntry(master, selectmode = "day",year=2022,month=9,date=27, foreground='black')
        self.start_date_picker.grid(row =3, column = 0, sticky="W")

        self.start_time_label = tkinter.Label(text="Enter start time (hh:mm)")
        self.start_time_label.grid(row =2, column = 1, pady=20, sticky="W")
        self.start_time_input = tkinter.Entry()
        self.start_time_input.insert(0, "09:30")
        self.start_time_input.grid(row=3, column=1, sticky="W")

        self.end_date_label = tkinter.Label(text="Enter end date")
        self.end_date_label.grid(row =2, column = 2, pady=20, sticky="W")
        self.end_date_picker = tkcalendar.DateEntry(master, selectmode = "day",year=2022,month=9,date=27, foreground='black')
        self.end_date_picker.grid(row =3, column = 2, sticky="W", padx=20)

        self.end_time_label = tkinter.Label(text="Enter end time (hh:mm)")
        self.end_time_label.grid(row =2, column = 3, pady=20, sticky="W")
        self.end_time_input = tkinter.Entry()
        self.end_time_input.insert(0, "16:00")
        self.end_time_input.grid(row=3, column=3, sticky="W")

        self.interval_label = tkinter.Label(text="Enter interval (1m, 2m, 5m, 1h, 1d)")
        self.interval_label.grid(row=4, column=0, sticky="W", pady=20,)
        self.interval = tkinter.Entry()
        self.interval.insert(0,'1m')
        self.interval.grid(row=5, column=0, sticky="W")

        self.data_provider_label = tkinter.Label(text="Select data provider")
        self.data_provider_label.grid(row=6, column=0, pady=20, sticky="W")
        data_providers = [provier.value for provier in DataProvider]
        self.selected_provider = tkinter.StringVar()
        for idx,provider in enumerate(data_providers):
            tkinter.Radiobutton(master, 
                        text=data_provider_label[provider],
                        padx = 20,
                        variable=self.selected_provider,
                        value=provider).grid(row=7+idx, column=0, sticky="W")
        
        self.indicators_label = tkinter.Label(text="Select indicators")
        self.indicators_label.grid(row=6, column=1, pady=20, sticky="W")
        self.selected_indicators = [tkinter.IntVar() for i in indicators]
        for idx, indicator in enumerate(indicators): 
            tkinter.Checkbutton(master,
                            text=indicator,
                            variable=self.selected_indicators[idx],
                            padx=20).grid(row=7, column=1+idx, sticky="W")

        self.indicators_label = tkinter.Label(text="Select candlestick patterns")
        self.indicators_label.grid(row=12, column=0, pady=20, sticky="W")
        self.selected_candlestick_patterns = [tkinter.IntVar() for i in candlestick_patterns]
        col_map = {}
        for idx, pattern in enumerate(candlestick_patterns): 
            row = 13+(idx%8)
            if row in col_map:
                col_map[row] += 1
            else: 
                col_map[row] = 0
            tkinter.Checkbutton(master,
                            text=talib_utilities.get_candlestick_pattern_label(pattern), 
                            variable=self.selected_candlestick_patterns[idx]
                            ).grid(row=row, column=col_map[row], sticky="W")
        
        self.submit_button = tkinter.Button(text='Plot Graph', command=self.on_submit_clicked)
        self.submit_button.grid(row=22, column=0, sticky="W", pady=20)


    def on_submit_clicked(self):
        symbol = self.symbol_input.get()
        start_date = self.start_date_picker.get_date()
        end_date = self.end_date_picker.get_date()
        start_time = datetime.strptime(self.start_time_input.get(), '%H:%M').time()
        end_time = datetime.strptime(self.end_time_input.get(), '%H:%M').time()
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)

        selected_interval = self.interval.get()
        provider = self.selected_provider.get()
        selected_candlestick_patterns = [candlestick_patterns[idx] for idx, indicator in enumerate(candlestick_patterns) if self.selected_candlestick_patterns[idx].get()]
        selected_indicators = [indicators[idx] for idx, indicator in enumerate(indicators) if self.selected_indicators[idx].get()]
        selected_momentum_indicators = []
        selected_volume_indicators = []
        for indicator in selected_indicators:
            if indicator in suggested_momentum_indicators:
                selected_momentum_indicators.append(indicator)
            if indicator in suggested_volume_indicators:
                selected_volume_indicators.append(indicator)

        ib_app = None
        if provider == DataProvider.ib_api:
            ib_app = IB()
            ib_app.connect(host='127.0.0.1', port=7497, clientId=1)

        params = get_bars_dto(provider, selected_interval, symbol, start_datetime, end_datetime, ib_app)
        data = api.get_bars(params)
        talib_utilities.add_candlestick_patterns_to_dataframe(selected_candlestick_patterns, data)
        talib_utilities.add_momentum_idicators_to_dataframe(selected_momentum_indicators, data)
        talib_utilities.add_volume_idicators_to_dataframe(selected_volume_indicators, data)
        plot_candlesticks(data, symbol, selected_candlestick_patterns)