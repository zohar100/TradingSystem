from strategy import DataProvider
from talib_utilities import candlestick_pattern_label
import tkinter
import tkcalendar

data_provider_label = {
    DataProvider.BARS_API: 'Our Api',
    DataProvider.YF_API: 'Yahoo Finance',
    DataProvider.POLY_API: 'Polygon',
    DataProvider.IB_API: 'Interactive Brokers'
}

candlestick_patterns = [
    "CDLDRAGONFLYDOJI",
    "CDLGRAVESTONEDOJI",
    "CDL3LINESTRIKE",
    "CDLENGULFING",
    "CDLEVENINGSTAR",
    "CDLEVENINGDOJISTAR",
    "CDLMORNINGSTAR",
    "CDLMORNINGDOJISTAR",
    "CDLHAMMER",
    "CDLINVERTEDHAMMER",
    "CDLSHOOTINGSTAR",
    "CDLHANGINGMAN",
    "CDLPIERCING"
]

indicators = ['VWAP', 'RSI']

class Viewer(tkinter.Frame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)

        self.symbol_input_label = tkinter.Label(text="Enter symbol")
        self.symbol_input_label.grid(row = 0, column = 0, sticky="W")
        self.symbol_input = tkinter.Entry()
        self.symbol_input.grid(row = 1, column = 0, sticky="W")

        self.date_label = tkinter.Label(text="Enter date")
        self.date_label.grid(row =2, column = 0, pady=20, sticky="W")
        self.date_picker = tkcalendar.DateEntry(master, selectmode = "day",year=2022,month=1,date=1, foreground='black')
        self.date_picker.grid(row =3, column = 0, sticky="W")

        self.start_time_label = tkinter.Label(text="Enter start time (hh:mm)")
        self.start_time_label.grid(row =2, column = 1, pady=20, sticky="W", padx=10)
        self.start_time_input = tkinter.Entry()
        self.start_time_input.insert(0, "09:30")
        self.start_time_input.grid(row=3, column=1, sticky="W", padx=10)

        self.end_time_label = tkinter.Label(text="Enter start time (hh:mm)")
        self.end_time_label.grid(row =2, column = 2, pady=20, sticky="W", padx=10)
        self.end_time_input = tkinter.Entry()
        self.end_time_input.insert(0, "16:00")
        self.end_time_input.grid(row=3, column=2, sticky="W", padx=10)

        self.data_provider_label = tkinter.Label(text="Select data provider")
        self.data_provider_label.grid(row=4, column=0, pady=20, sticky="W")
        data_providers = [provier.value for provier in DataProvider]
        self.selected_provider = tkinter.StringVar()
        for idx,provider in enumerate(data_providers):
            tkinter.Radiobutton(master, 
                        text=data_provider_label[provider],
                        padx = 20,
                        variable=self.selected_provider,
                        value=provider).grid(row=5+idx, column=0, sticky="W")
        
        self.indicators_label = tkinter.Label(text="Select indicators")
        self.indicators_label.grid(row=4, column=1, pady=20, sticky="W")
        self.selected_indicators = [tkinter.IntVar() for i in indicators]
        for idx, indicator in enumerate(indicators): 
            tkinter.Checkbutton(master,
                            text=indicator,
                            variable=self.selected_indicators[idx],
                            padx=20).grid(row=5, column=1+idx, sticky="W")

        self.indicators_label = tkinter.Label(text="Select candlestick patterns")
        self.indicators_label.grid(row=10, column=0, pady=20, sticky="W")
        self.selected_candlestick_patterns = [tkinter.IntVar() for i in candlestick_patterns]
        col_map = {}
        for idx, pattern in enumerate(candlestick_patterns): 
            row = 11+(idx%8)
            if row in col_map:
                col_map[row] += 1
            else: 
                col_map[row] = 0
            tkinter.Checkbutton(master,
                            text=candlestick_pattern_label[pattern], 
                            variable=self.selected_candlestick_patterns[idx]
                            ).grid(row=row, column=col_map[row], sticky="W")
        
        self.submit_button = tkinter.Button(text='Plot Graph', command=self.on_submit_clicked)
        self.submit_button.grid(row=20, column=0, sticky="W", pady=20)


    def on_submit_clicked(self):
        symbol = self.symbol_input.get()
        date = self.date_picker.get_date()
        start_time = self.start_time_input.get()
        end_time = self.end_time_input.get()
        provider = self.selected_provider.get()
        selected_indicators = [indicators[idx] for idx, indicator in enumerate(indicators) if self.selected_indicators[idx].get()]
        selected_candlestick_patterns = [candlestick_patterns[idx] for idx, indicator in enumerate(candlestick_patterns) if self.selected_candlestick_patterns[idx].get()]

root = tkinter.Tk()
root.geometry("650x750")
root.title("Viewer")

viewer = Viewer(root)
viewer.mainloop()