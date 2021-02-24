from coinbaseClient.coinbase_pro_client import get_accounts, get_private_client, get_public_client
from Config.config import TARGET_PERCENTS, CB_CREDENTIALS, REBALANCE_TARGET, REBALANCE_TOLERANCE
from Data.product import get_products_for_quote_currency_info
from Data.account_format import format_account_and_get_portfolio_value
from Data.change_vs_portfolio import set_and_sort_crypto_change_vs_portfolio
from Trades.execute_trades import handle_trades
from Trades.generate_trades import generate_trade

import datetime


def main(event="", context=""):
    private_client = get_private_client(CB_CREDENTIALS)
    public_client = get_public_client(CB_CREDENTIALS['URL'])
    print(f'--------START TIME {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-----------')
    quote_currency = 'USD'

    products_to_quote_currency_info = get_products_for_quote_currency_info(quote_currency, public_client)
    accounts = get_accounts(private_client)
    cryptos, portfolio_value = format_account_and_get_portfolio_value(accounts, quote_currency, products_to_quote_currency_info, private_client)
    del products_to_quote_currency_info
    del accounts
    sorted_by_growth_cryptos, max_change_vs_portfolio, quote_currency_amount = set_and_sort_crypto_change_vs_portfolio(cryptos, portfolio_value, quote_currency)
    del cryptos
    print('------------------STATS---------------------')
    print(f"Target Percent: {REBALANCE_TARGET}, Tolerance: {REBALANCE_TOLERANCE}, Portfolio Value: {portfolio_value}, Max Change: {max_change_vs_portfolio}, {quote_currency}: {quote_currency_amount}")
    print('------------------PORTFOLIO---------------------')
    sell_trades = []
    buy_trades = []
    cryptos_in_account = [crypto['Crypto'] for crypto in sorted_by_growth_cryptos]
    for crypto in sorted_by_growth_cryptos:
        print(f'Crypto: {crypto["Crypto"]}, Price: {crypto["Price"]}, Market Value: {round(crypto["MarketValue"],2)}, Percent: {round(crypto["CurrentPercent"],4)}, Target Percent: {crypto["TargetPercent"]}, Percent Growth VS PTF = {round(crypto.get("ChangeVsPortfolio"),4)}')
        if max_change_vs_portfolio >= REBALANCE_TARGET:
            trade, quote_currency_amount = generate_trade(crypto, quote_currency, portfolio_value, quote_currency_amount)
            if trade:
                if trade['side'] == 'buy':
                    buy_trades.append(trade)
                elif trade['side'] == 'sell':
                    sell_trades.append(trade)
    for target_crypto in TARGET_PERCENTS.keys():
        if target_crypto not in cryptos_in_account:
            funds = (TARGET_PERCENTS[target_crypto]/100)*portfolio_value
            print(f'Funds Needed: {funds}')
            if funds > quote_currency_amount:
                funds = quote_currency_amount
            trade = {'type': 'market',
                     'side': 'buy',
                     'product_id': f'{target_crypto}-{quote_currency}',
                     'funds': round(funds, 2)
                    }
            buy_trades.append(trade)
    del sorted_by_growth_cryptos
    handle_trades(private_client=private_client, buy_trades=buy_trades, sell_trades=sell_trades)


    del buy_trades
    del sell_trades
    print(f'--------END TIME {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-----------')

main()
