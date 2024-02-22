from order import Order

INITIAL_CAPITAL_USDT = 15_000
MAXIMUM_PERCENTAGE_DECLINE = 2.0
THRESHOLD_PERCENTAGE_PROFIT = 4.0


def trading_session(price_stats, num_prices, initial_capital, capital_division_ration):
    orders_queue = []
    net_gain = 0
    capital_portion = initial_capital * capital_division_ration
    capital_at_the_end = initial_capital
    for idx in range(num_prices):
        current_timestamp = price_stats['TIMESTAMP'][idx]
        open_price = price_stats['OPEN'][idx]

        close_price = price_stats['CLOSE'][idx]

        if len(orders_queue) > 0:
            tail_order = orders_queue[0]
            mean_price = (open_price + close_price) / 2
            order_percentage_difference = (mean_price - tail_order.buying_price) * 100 / tail_order.buying_price
            if order_percentage_difference < 0 and abs(order_percentage_difference) >= MAXIMUM_PERCENTAGE_DECLINE:
                capital_portion_with_gain = tail_order.amount_of_asset_bought * close_price
                tail_order.execute(close_price, current_timestamp)
                net_gain += (tail_order.amount_of_asset_bought * close_price - capital_portion)
                orders_queue.pop(0)
                capital_at_the_end += capital_portion_with_gain
            elif order_percentage_difference > 0 and order_percentage_difference >= THRESHOLD_PERCENTAGE_PROFIT:
                capital_portion_with_gain = tail_order.amount_of_asset_bought * close_price
                tail_order.execute(close_price, current_timestamp)
                net_gain += (tail_order.amount_of_asset_bought * close_price - capital_portion)
                orders_queue.pop(0)
                capital_at_the_end += capital_portion_with_gain

        if capital_at_the_end > 0:
            one_usdt_asset_amount = 1 / open_price
            orders_queue.append(Order(open_price, current_timestamp, capital_portion * one_usdt_asset_amount))
            capital_at_the_end -= capital_portion
    capital_at_the_end += sum(order.buying_price * order.amount_of_asset_bought for order in orders_queue)
    return (f'initial capital {round(initial_capital, 2)}$ net gain {round(net_gain, 2)}$ capital at the end '
            f'{round(capital_at_the_end, 2)}$')
