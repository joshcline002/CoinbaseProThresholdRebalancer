from coinbaseClient.coinbase_pro_client import get_accounts, place_order
from Config.config import REBALANCE_TARGET, REBALANCE_TOLERANCE, FEE_PERCENT, ENABLE_TRADING
from Data.product import get_products_for_quote_currency_info
from Data.account_format import format_account_and_get_portfolio_value
from Data.change_vs_portfolio import set_and_sort_crypto_change_vs_portfolio

import datetime


def main(event="", context=""):
    print(f'--------START TIME {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-----------')
    quote_currency = 'USD'

    products_to_quote_currency_info = get_products_for_quote_currency_info(quote_currency)
    accounts = get_accounts()
    cryptos, portfolio_value = format_account_and_get_portfolio_value(accounts, quote_currency, products_to_quote_currency_info)
    del products_to_quote_currency_info
    del accounts
    sorted_by_growth_cryptos, max_change_vs_portfolio, quote_currency_amount = set_and_sort_crypto_change_vs_portfolio(cryptos, portfolio_value, quote_currency)
    print('------------------STATS---------------------')
    print(f"Target Percent: {REBALANCE_TARGET}, Tolerance: {REBALANCE_TOLERANCE}, Portfolio Value: {portfolio_value}, Max Change: {max_change_vs_portfolio}, {quote_currency}: {quote_currency_amount}")
    print('------------------PORTFOLIO---------------------')
    sell_trades = []
    buy_trades = []
    for crypto in sorted_by_growth_cryptos:
        print(f'Crypto: {crypto["Crypto"]}, Price: {crypto["Price"]}, Market Value: {round(crypto["MarketValue"],2)}, Percent: {round(crypto["CurrentPercent"],4)}, Target Percent: {crypto["TargetPercent"]}, Percent Growth VS PTF = {round(crypto.get("ChangeVsPortfolio"),2)}')
    if max_change_vs_portfolio >= REBALANCE_TARGET:
        for crypto in cryptos:
            if crypto["Crypto"] == quote_currency:
                continue
            target_percent = crypto['TargetPercent']
            if  target_percent != 0:
                change_vs_portfolio = crypto['ChangeVsPortfolio']
                if not (abs(change_vs_portfolio) >= REBALANCE_TOLERANCE):
                    continue
                if change_vs_portfolio > 0:
                    side = 'sell'
                else:
                    side = 'buy'
                current_percent = crypto['CurrentPercent']
                percent_difference = current_percent - target_percent
                shares = abs(round((percent_difference/current_percent)*crypto['Balance'], crypto['shares_round_to_digit']))
                quote_amount_needed = abs(round((percent_difference/100)*portfolio_value, crypto[f'{quote_currency}_round_to_digit']))
                if side == 'buy':
                    if quote_amount_needed > quote_currency_amount:
                        quote_amount_needed = quote_currency_amount
            else:
                side = 'sell'
                shares = crypto['Balance']
                quote_amount_needed = crypto['MarketValue']
            if shares < crypto['base_min_size'] and side == 'sell':
                continue
            elif side == 'sell':
                quote_currency_amount = quote_currency_amount + quote_amount_needed*(1-FEE_PERCENT/100)
            if quote_amount_needed < crypto['min_market_funds'] and side == 'buy':
                continue
            elif side == 'buy':
                quote_currency_amount = quote_currency_amount - quote_amount_needed
            trade = {'type': 'market',
                     'side': side,
                     'product_id': f'{crypto["Crypto"]}-{quote_currency}',
                     'size': shares,
                     'funds': quote_amount_needed
                    }
            if side == 'buy':
                buy_trades.append(trade)
            elif side == 'sell':
                sell_trades.append(trade)

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
                response = place_order(side=trade['side'], product_id=trade['product_id'], funds=trade['funds'])
        for trade in buy_trades:
            print(trade)
            if ENABLE_TRADING:
                response = place_order(side=trade['side'], product_id=trade['product_id'], funds=trade['funds'])
    else:
        print(f"No asset exceeding {REBALANCE_TARGET} no trades needed.")



    print(f"Ending {quote_currency}: {quote_currency_amount}")
    print(f'--------END TIME {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-----------')

main()
