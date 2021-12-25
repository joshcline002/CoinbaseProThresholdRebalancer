from coinbase_client.my_coinbase_pro_client import place_order
from trader_config.config import ENABLE_TRADING, TARGET_PERCENTS, REBALANCED_TARGET


def handle_trades(private_client, buy_trades, sell_trades):
    print_trade_title()
    buy_trades.reverse()
    if len(buy_trades) > 0 or len(sell_trades) > 0:
        execute_sell_trades(private_client, sell_trades)
        execute_buy_trades(buy_trades, private_client)
    else:
        print(f"No asset exceeding {REBALANCED_TARGET} no trades needed.")


def print_trade_title():
    if ENABLE_TRADING:
        trade_title = 'TRADES EXECUTED'
    else:
        trade_title = 'TRADES TO EXECUTE'
    print(f'------------------{trade_title}---------------------')


def execute_buy_trades(buy_trades, private_client):
    for trade in buy_trades:
        print(trade)
        if ENABLE_TRADING:
            response = place_order(private_client=private_client, side=trade['side'],
                                   product_id=trade['product_id'], funds=trade['funds'])
            print(response)


def execute_sell_trades(private_client, sell_trades):
    for trade in sell_trades:
        print(trade)
        if ENABLE_TRADING:
            if trade['product_id'].split('-')[0] not in TARGET_PERCENTS.keys():
                response = place_order(private_client=private_client, side=trade['side'],
                                       product_id=trade['product_id'], size=trade['size'])
            else:
                response = place_order(private_client=private_client, side=trade['side'],
                                       product_id=trade['product_id'], funds=trade['funds'])
            print(response)
