from typing import Dict, List

INITIAL_CAPITAL_USD = "INITIAL_CAPITAL_USD"
CAPITAL_PORTIONS = "CAPITAL_PORTIONS"
MAX_PERCENTAGE_DECLINE = "MAX_PERCENTAGE_DECLINE"
TIMESTAMP = 'TIMESTAMP'
OPEN = 'OPEN'
CLOSE = 'CLOSE'
FIRST_LINE_TRADING_DATA = 'OPEN,CLOSE,TIMESTAMP'


def valid_csv_format(trading_data_str: str) -> bool:
    if trading_data_str is None:
        return False
    trading_data_arr = convert_trading_str_to_array(trading_data_str)
    if len(trading_data_arr) < 1:
        return False
    if FIRST_LINE_TRADING_DATA not in trading_data_arr[0]:
        return False

    for i in range(1, len(trading_data_arr)):
        line = trading_data_arr[i]
        data_arr = line.split(",")
        if len(data_arr) != 3:
            return False
        for el in data_arr:
            if el is not None and not el.replace(".", "1").isdigit():
                return False
    return True


def process_csv_file(trading_data_str: str) -> Dict:
    dict_info = {
        INITIAL_CAPITAL_USD: 15_000,
        CAPITAL_PORTIONS: 15,
        MAX_PERCENTAGE_DECLINE: 4,
        OPEN: [],
        CLOSE: [],
        TIMESTAMP: []
    }
    if trading_data_str is None:
        return dict_info
    trading_data_arr = convert_trading_str_to_array(trading_data_str)
    for i in range(1, len(trading_data_arr)):
        if len(trading_data_arr[i]) == 0:
            continue
        split_line = trading_data_arr[i].split(",")
        dict_info[OPEN].append(float(split_line[0]))
        dict_info[CLOSE].append(float(split_line[1]))
        dict_info[TIMESTAMP].append(float(split_line[2]))

    return dict_info


def convert_trading_str_to_array(trading_data_str: str) -> List[str]:
    trading_data_str = trading_data_str.replace("\r", "")
    trading_data_arr = trading_data_str.split("\n")
    # remove empty lines at the end
    while len(trading_data_arr) and len(trading_data_arr[-1]) == 0:
        trading_data_arr.pop()
    return trading_data_arr
