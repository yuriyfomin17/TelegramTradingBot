from binance import Client
from constants import *
from helper_functions import convert_binance_timestamp_to_date

BINANCE_API_KEY = "PASTE_YOUR_BINANCE_API_KEY"
BINANCE_API_SECRET = "PASTE_YOUR_BINANCE_API_SECRET"
TIMESTAMP_IDX = 0
OPEN_PRICE_IDX = 1
CLOSING_PRICE_IDX = 4
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)


def fetch_trading_date_for_one_day_interval_from_binance(start_date, end_date):
    klines_1_day = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, start_str=start_date,
                                                end_str=end_date)
    return {
        OPEN_PRICE_KEY: [float(el[OPEN_PRICE_IDX]) for el in klines_1_day],
        CLOSE_PRICE_KEY: [float(el[CLOSING_PRICE_IDX]) for el in klines_1_day],
        TIMESTAMP_KEY: [convert_binance_timestamp_to_date(el[TIMESTAMP_IDX]) for el in klines_1_day]
    }
