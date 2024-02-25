from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import matplotlib

from constants import *

VALID_DATE_FORMAT = "%Y-%m-%d"

matplotlib.use('Agg')


def convert_binance_timestamp_to_date(binance_timestamp):
    timestamp_seconds = binance_timestamp / 1000
    date_object = datetime.utcfromtimestamp(timestamp_seconds)
    return date_object.strftime("%m-%d")


def is_valid_initial_capital(str_number: str):
    return str_number is not None and str_number.isdigit() and 1000 <= float(str_number)


def is_valid_stop_loss_percentage(str_number: str):
    return str_number is not None and str_number.replace(".", "1").isdigit() and 0 < float(str_number) <= 100


def is_valid_start_and_end_date(start_date: str, end_date: str):
    if start_date is None or end_date is None:
        return False
    try:
        parsed_start_date = datetime.strptime(start_date, VALID_DATE_FORMAT)
        parsed_end_date = datetime.strptime(end_date, VALID_DATE_FORMAT)
        return parsed_start_date < parsed_end_date
    except ValueError:
        return False


def convert_to_trading_information(trading_information: str):
    # "15000, 2, 2024-02-01, 2024-02-20"
    trading_information = trading_information.replace(" ", "")
    trading_information_arr = trading_information.split(",")
    if len(trading_information_arr) != 4:
        return None
    initial_capital_usd, stop_loss_percentage, start_date, end_date = trading_information_arr
    if not is_valid_initial_capital(initial_capital_usd):
        return None
    if not is_valid_stop_loss_percentage(stop_loss_percentage):
        return None
    if not is_valid_start_and_end_date(start_date, end_date):
        return None

    return {
        INITIAL_CAPITAL_KEY: float(initial_capital_usd),
        STOP_LOSS_PERCENTAGE_KEY: float(stop_loss_percentage),
        START_DATE_KEY: start_date,
        END_DATE_KEY: end_date
    }


def is_valid_trading_info(trading_info: dict) -> bool:
    return (trading_info[INITIAL_CAPITAL_KEY] is not None and
            trading_info[STOP_LOSS_PERCENTAGE_KEY] is not None and
            trading_info[START_DATE_KEY] is not None and
            trading_info[END_DATE_KEY] is not None)


def create_net_gain_graph(net_gain_array, timestamp_arr, start_date, end_date):
    df = pd.DataFrame()
    df['net_gain'] = net_gain_array
    df['timestamp'] = timestamp_arr
    df.set_index('timestamp', inplace=True)
    plt.figure(figsize=(20, 6))
    plt.xticks(rotation=45)
    plt.plot(df['net_gain'], label='User Net Gain in USA dollar', marker='o')
    plt.title(f'Net Gain in USA Dollar - {start_date} to {end_date}')
    plt.xlabel('Date')
    plt.ylabel('Net Gain In Dollar')
    plt.legend()
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    return buf
