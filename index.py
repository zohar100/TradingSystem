import csv
from datetime import *
import yfinance
import pandas as pd
from utilities import utilities
from trading_utilities import trading_utilities
from trading_calculations import trading_calculations
from candlestick_patterns import candlestick_patterns
from ib_insync import *
import pytz

tz_ny = pytz.timezone("US/Eastern")
pre_market_start_time = time(9,30)
market_start_time = time(9,30)
market_end_time = time(16)

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
            new_bar[field] = bar[field.lower()].astimezone(tz_ny)
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

start_date = date(2022, 1, 1)
end_date = date(2022, 11, 21)
dates = utilities.daterange(start_date, end_date)
for today_date in dates:
    print(today_date)

    if not trading_utilities.is_trading_day(today_date):
        print("Not trading day")
        continue

    last_trading_date = trading_utilities.get_last_trading_date(today_date)

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

    # Everything fine we are about to make order
    take_profit = min(last_trading_date_data["Low"][:-5]) if market_direction == "BUY" else max(last_trading_date_data["High"][:-5])
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

    trading_candiles = today_data.iloc[:-10]
    candlestick_pattern = None
    candlestick_close_price = None
    candlestick_time = None

    for index, bar in trading_candiles.iloc[:5].iterrows():
        if not candlestick_pattern:
            candlestick_pattern = check_for_candlestick_patterns(trading_candiles[:index], market_direction)
            if candlestick_pattern:
                candlestick_close_price = bar["Close"]
                candlestick_time = index

    order["candlestick_pattern"] = candlestick_pattern if candlestick_pattern else "N/A"
    order["candlestick_close_price"] = candlestick_close_price if candlestick_close_price else "N/A"
    order["candlestick_time"] = candlestick_time if candlestick_time else "N/A"

    last_bar_index = trading_candiles.index[-1]
    for index, bar in trading_candiles.iterrows():

        pl = trading_utilities.check_pl(market_direction, bar, take_profit)
        if pl:
            order["lowest_point"] = min(trading_candiles["Low"][:index])
            order["highest_point"] = max(trading_candiles["High"][:index])
            order["exit_at_price"] = take_profit
            order["exit_at_time"] = index
            order["pl"] = trading_calculations.pl(order["buy_point"], quantity, take_profit, market_direction, 1.8)
            orders.append(order)
            break

        if index == last_bar_index:
            order["lowest_point"] = min(trading_candiles["Low"][:index])
            order["highest_point"] = max(trading_candiles["High"][:index])
            order["exit_at_price"] = bar["Close"]
            order["exit_at_time"] = index
            order["pl"] = trading_calculations.pl(order["buy_point"], quantity, bar["Close"], market_direction, 1.8)
            orders.append(order)

keys = orders[0].keys()
with open(f'orders-{start_date.strftime("%Y")}.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(orders)
