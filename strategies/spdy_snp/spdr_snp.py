
from datetime import date, datetime
from trading_utilities import market_end_time
from ib_insync import Contract, IB

class spdr_snp:
    def __init__(self, start_date: date, end_date: date) -> None:
        self.start_date = start_date
        self.end_date = end_date

        self.ib = IB()
        self.ib.connect(host='127.0.0.1', port=7497, clientId=1)

    def get_spy_data_from_ib(self):
        date_and_time = datetime.combine(self.end_date, market_end_time)
        formatted_end_date = date_and_time.strftime("%Y%m%d %H:%M:%S US/Eastern")
        spy_ticker = Contract(symbol="SPY", secType="STK", exchange="IBKRATS", currency="USD")
        
        data = self.ib.reqHistoricalData(spy_ticker, formatted_end_date, f"2 D", "5 mins", "TRADES", False)
        dict_data = [format_ib_bar(bar.__dict__) for bar in data]
        df_data = pd.DataFrame(dict_data).set_index('Date')
        return df_data
