from decorators.utils import timeit
from coinbaseClient.coinbase_pro_client import place_order
from Config.config import ENABLE_TRADING, TARGET_PERCENTS, REBALANCE_TARGET


def handle_trades(private_client, buy_trades, sell_trades):
    if ENABLE_TRADING:
        trade_title = 'TRADES EXECUTED'
    else:
        trade_title = 'TRADES TO EXECUTE'
    print(f'------------------{trade_title}---------------------')
    buy_trades.reverse()
    if len(buy_trades) > 0 or len(sell_trades) > 0:
        for trade in sell_trades:
            print(trade)
            if ENABLE_TRADING:
                if trade['product_id'].split('-')[0] not in TARGET_PERCENTS.keys():
                    response = place_order(private_client=private_client, side=trade['side'], product_id=trade['product_id'], size=trade['size'])
                else:
                    response = place_order(private_client=private_client, side=trade['side'], product_id=trade['product_id'], funds=trade['funds'])
                print(response)
        for trade in buy_trades:
            print(trade)
            if ENABLE_TRADING:
                response = place_order(private_client=private_client, side=trade['side'], product_id=trade['product_id'], funds=trade['funds'])
                print(response)
    else:
        print(f"No asset exceeding {REBALANCE_TARGET} no trades needed.")
