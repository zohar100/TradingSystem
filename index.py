import csv
from datetime import *
import talib
from talib_utilities import talib_utilities
import pandas as pd
from utilities import utilities
from trading_utilities import trading_utilities, new_york_timezone, market_end_time, market_start_time, pre_market_start_time
from trading_calculations import trading_calculations
from candlestick_patterns import candlestick_patterns
from ib_insync import *


def check_direction(yesterday_close: float, today_open: float, plus: float):
    if yesterday_close < today_open - plus:
        return "SELL"
    if yesterday_close > today_open + plus:
        return "BUY"

def check_market_size_gap(gap: float, market_size: float):
    return gap < (market_size * 0.85) and gap > (market_size * 0.15)

def check_gap(gap: float):
    return gap <= 3

def calc_quantity(risk, today_open):
    return round(risk / today_open)

def format_ib_bar(bar: dict):
    fields = ["Date", "High", "Open", "Low", "Close", "Volume"]
    new_bar = {}
    for field in fields:
        if field == "Date":
            new_bar[field] = bar[field.lower()].astimezone(new_york_timezone)
        else:
            new_bar[field] = bar[field.lower()]
    return new_bar

def get_spy_data_from_ib(end_date: date):
    date_and_time = datetime.combine(end_date, market_end_time)
    formatted_end_date = date_and_time.strftime("%Y%m%d %H:%M:%S US/Eastern")
    spy_ticker = Contract(symbol="SPY", secType="STK", exchange="IBKRATS", currency="USD")
    
    data = ib.reqHistoricalData(spy_ticker, formatted_end_date, f"2 D", "1 min", "TRADES", False)
    dict_data = [format_ib_bar(bar.__dict__) for bar in data]
    df_data = pd.DataFrame(dict_data).set_index('Date')
    return df_data

def check_for_candlestick_patterns(bars: pd.DataFrame, direction: str):
    if direction == "BUY":
        hummer = candlestick_patterns.hummer(bars)
        if hummer: 
            return "HUMMER"
        okar_buy = candlestick_patterns.okar_buy(bars)
        if okar_buy:
            return "OKAR_BUY"
    if direction == "SELL":
        shooting = candlestick_patterns.shooting_star(bars)
        if shooting:
            return "SHOOTING_STAR"
        okar_sell = candlestick_patterns.okar_sell(bars)
        if okar_sell:
            return "OKAR_SELL"

    return None

ib = IB()
ib.connect(host='127.0.0.1', port=7497, clientId=1)

orders: list[dict] = []

start_date = date(2022, 1,1)
end_date = date(2022, 11, 25)
dates = utilities.daterange(start_date, end_date)
for today_date in dates:
    print(today_date)

    if not trading_utilities.is_trading_day(today_date):
        print("Not trading day")
        continue

    last_trading_date = trading_utilities.get_last_trading_date(today_date)

    # col_names = ["Date","High","Open","Low","Close","Volume"]
    # all_data = pd.read_csv('./data/SPY/SPY-2022.csv', skiprows=196068, names=col_names, index_col="Date")
    # all_data.index = pd.to_datetime(all_data.index)
    all_data: pd.DataFrame = get_spy_data_from_ib(today_date)
    all_data.index = all_data.index.tz_localize(None)
    
    print("Saving data....")
    try:
        pd.read_csv(f'./data/SPY/SPY-{start_date.strftime("%Y")}.csv', index_col="Date").append(all_data).drop_duplicates().to_csv(f'./data/SPY/SPY-{start_date.strftime("%Y")}.csv', encoding='utf-8', index=True)
    except FileNotFoundError:
        all_data.to_csv(f'./data/SPY/SPY-{start_date.strftime("%Y")}.csv', encoding='utf-8', index=True)
    print("Data saved")

    last_trading_start_date_time = datetime.combine(last_trading_date, market_start_time)
    last_trading_end_date_time = datetime.combine(last_trading_date, market_end_time)
    last_trading_date_data = all_data.loc[last_trading_start_date_time:last_trading_end_date_time]

    today_start_date_time = datetime.combine(today_date, market_start_time)
    today_end_date_time = datetime.combine(today_date, market_end_time)
    today_data = all_data.loc[today_start_date_time:today_end_date_time]

    pre_market_start_date_time = datetime.combine(today_date, pre_market_start_time)
    pre_market_end_date_time = datetime.combine(today_date, market_start_time)
    pre_market_data = all_data.loc[pre_market_start_date_time:pre_market_end_date_time]

    yesterday_close = last_trading_date_data["Close"][-1]
    yesterday_high = max(last_trading_date_data["High"])
    yesterday_low = min(last_trading_date_data["Low"])
    today_open = today_data["Open"][0]

    market_direction = check_direction(yesterday_close, today_open, 0.20)
    if not market_direction:
        print("We dont make a trade today - market_direction")
        continue
    
    gap = trading_calculations.gap_percentage(today_open, yesterday_close, market_direction)
    market_size = trading_calculations.market_size_percentage(yesterday_high, yesterday_low)

    is_gap_valid = check_gap(gap)
    if not is_gap_valid:
        print("We dont make a trade today - gap_valid")
        continue

    is_market_size_gap = check_market_size_gap(gap, market_size)
    if not is_market_size_gap:
        print("We dont make a trade today - market_size_gap")
        continue

    print(f"We going to make a {market_direction} trade")

    last_trading_five_min_time = time(15, 55)
    last_trading_five_min_start = datetime.combine(last_trading_date, last_trading_five_min_time)
    last_trading_day_data_last_five_min = last_trading_date_data.loc[last_trading_five_min_start:last_trading_end_date_time]
    # Everything fine we are about to make order
    if market_direction == 'BUY':
        take_profit = min(last_trading_day_data_last_five_min["Low"])
    elif market_direction == 'SELL':
        take_profit = max(last_trading_day_data_last_five_min["High"])

    risk = 16000
    quantity = calc_quantity(risk, today_open)

    print(f"That is our take profirt {take_profit}")
    print(f"That is our quantity {quantity}")

    order = {
        "date": today_date,
        "take_profit": take_profit,
        "buy_point": today_open,
        "action": market_direction,
        "risk": risk,
        "quantity": quantity,
        "gap": gap,
        "volume": sum(pre_market_data["Volume"]) * 100
    }

    trading_end_time = time(15, 50)
    trading_candles_start_date_time = datetime.combine(today_date, market_start_time)
    trading_candles_end_date_time = datetime.combine(today_date, trading_end_time)
    trading_candles = all_data.loc[trading_candles_start_date_time:trading_candles_end_date_time]

    first_five_mins_bars = trading_candles.iloc[:5]
    op = first_five_mins_bars['Open']
    hi = first_five_mins_bars['High']
    lo = first_five_mins_bars['Low']
    cl = first_five_mins_bars['Close']
    
    patterns = {}
    candle_names = talib.get_function_groups()['Pattern Recognition']
    for candle in candle_names:
        patterns[candle] = getattr(talib, candle)(op, hi, lo, cl)

    patterns_to_save = []
    for patten, _data in patterns.items():
        for _time, is_pattern in _data.items():
            if is_pattern:
                pattern_to_save = {
                    "time": str(_time),
                    "pattern": talib_utilities.get_candlestick_pattern_label(patten),
                    "direction": "SELL" if is_pattern < 0 else "BUY"
                }
                patterns_to_save.append(pattern_to_save)

    last_bar_index = trading_candles.index[-1]
    for index, bar in trading_candles.iterrows():

        pl = trading_utilities.check_pl(market_direction, bar, take_profit)
        if pl:
            order["lowest_point"] = min(trading_candles["Low"][:index])
            order["highest_point"] = max(trading_candles["High"][:index])
            order["exit_at_price"] = take_profit
            order["exit_at_time"] = index
            order["pl"] = trading_calculations.pl(order["buy_point"], quantity, take_profit, market_direction, 1.8)
            order["pattern"] = "N/A"
            order["pattern_time"] = "N/A"
            order["pattern_direction"] = "N/A"
            if len(patterns_to_save) != 0:
                for pattern in patterns_to_save:
                    order["pattern"] = pattern["pattern"]
                    order["pattern_time"] = pattern["time"]
                    order["pattern_direction"] = pattern["direction"]

            orders.append(order)
            break
        
        if index == last_bar_index:
            order["lowest_point"] = min(trading_candles["Low"][:index])
            order["highest_point"] = max(trading_candles["High"][:index])
            order["exit_at_price"] = bar["Close"]
            order["exit_at_time"] = index
            order["pl"] = trading_calculations.pl(order["buy_point"], quantity, bar["Close"], market_direction, 1.8)
            order["pattern"] = "N/A"
            order["pattern_time"] = "N/A"
            order["pattern_direction"] = "N/A"
            if len(patterns_to_save) != 0:
                for pattern in patterns_to_save:
                    order["pattern"] = pattern["pattern"]
                    order["pattern_time"] = pattern["time"]
                    order["pattern_direction"] = pattern["direction"]

            orders.append(order)
                    

keys = orders[0].keys()
with open(f'orders-{start_date.strftime("%Y")}.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(orders)
