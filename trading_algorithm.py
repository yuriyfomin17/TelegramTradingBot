from constants import *
from order import Order
from collections import deque

THRESHOLD_PERCENTAGE_PROFIT = 4.0


def execute_oldest_order(capital_at_the_end, capital_portion, close_price, current_timestamp, net_gain, orders_queue,
                         tail_order):
    capital_portion_with_gain = tail_order.amount_of_asset_bought * close_price
    tail_order.execute(close_price, current_timestamp)
    net_gain += (tail_order.amount_of_asset_bought * close_price - capital_portion)
    orders_queue.popleft()
    capital_at_the_end += capital_portion_with_gain
    return capital_at_the_end, net_gain


def trading_session(price_stats, num_prices, initial_capital, stop_loss_percentage):
    orders_queue = deque()
    net_gain = 0
    capital_per_trade = 1000
    capital_at_the_end = initial_capital
    num_profitable_trades = 0
    num_losing_trades = 0
    net_gain_array = []
    timestamp_arr = []
    for idx in range(num_prices):
        current_timestamp = price_stats[TIMESTAMP_KEY][idx]
        open_price = price_stats[OPEN_PRICE_KEY][idx]

        close_price = price_stats[CLOSE_PRICE_KEY][idx]

        if len(orders_queue) > 0:
            tail_order = orders_queue[0]
            order_percentage_difference = (close_price - tail_order.buying_price) * 100 / tail_order.buying_price
            if order_percentage_difference < 0 and abs(order_percentage_difference) > stop_loss_percentage:
                capital_at_the_end, net_gain = execute_oldest_order(capital_at_the_end, capital_per_trade, close_price,
                                                                    current_timestamp, net_gain, orders_queue,
                                                                    tail_order)
                num_losing_trades += 1
            elif order_percentage_difference > 0 and order_percentage_difference >= THRESHOLD_PERCENTAGE_PROFIT:
                capital_at_the_end, net_gain = execute_oldest_order(capital_at_the_end, capital_per_trade, close_price,
                                                                    current_timestamp, net_gain, orders_queue,
                                                                    tail_order)
                num_profitable_trades += 1
        if capital_at_the_end > 0:
            one_usdt_asset_amount = 1 / open_price
            orders_queue.append(Order(open_price, current_timestamp, capital_per_trade * one_usdt_asset_amount))
            capital_at_the_end -= capital_per_trade
        net_gain_array.append(net_gain)
        timestamp_arr.append(current_timestamp)
    capital_at_the_end += sum([order.buying_price * order.amount_of_asset_bought for order in orders_queue])
    percentage_profit = round((net_gain * 100 / initial_capital), 2)
    return (f'✅Finished!\n'
            f'Initial capital = {round(initial_capital, 2)}$\n'
            f'Net gain = {round(net_gain, 2)}$\n'
            f'Capital at the end = {round(capital_at_the_end, 2)}$\n'
            f'Capital percentage profit = {percentage_profit}%\n'
            f'Number of profitable trades = {num_profitable_trades}\n'
            f'Number of losing trades = {num_losing_trades}'), net_gain_array
