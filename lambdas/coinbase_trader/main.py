import datetime

# pylint: disable=import-error
from Trades.execute_trades import handle_trades
from Trades.generate_trades import generate_trade
from coinbase_client.my_coinbase_pro_client import get_accounts, get_private_client, \
    get_public_client
from data.account_format import format_account_and_get_portfolio_value
from data.change_vs_portfolio import set_and_sort_crypto_change_vs_portfolio
from data.product import get_products_for_quote_currency_info
from trader_config.config import TARGET_PERCENTS, CB_CREDENTIALS, REBALANCED_TARGET, \
    REBALANCED_TOLERANCE


# pylint: disable-next=too-many-locals
def main(_event="", _context=""):
    private_client = get_private_client(CB_CREDENTIALS)
    public_client = get_public_client(CB_CREDENTIALS['URL'])
    print(f'--------START TIME {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-----------')
    quote_currency = 'USD'

    products_to_quote_currency_info = get_products_for_quote_currency_info(quote_currency,
                                                                           public_client)
    accounts = get_accounts(private_client)
    cryptos, portfolio_value = \
        format_account_and_get_portfolio_value(accounts, quote_currency,
                                               products_to_quote_currency_info, private_client)
    del products_to_quote_currency_info
    del accounts
    sorted_by_growth_cryptos, max_change_vs_portfolio, quote_currency_amount = \
        set_and_sort_crypto_change_vs_portfolio(cryptos, portfolio_value, quote_currency)
    del cryptos
    print('------------------STATS---------------------')
    print(
        f"Target Percent: {REBALANCED_TARGET}, Tolerance: {REBALANCED_TOLERANCE}, "
        f"Portfolio Value: {portfolio_value}, Max Change: {max_change_vs_portfolio}, "
        f"{quote_currency}: {quote_currency_amount}")
    print('------------------PORTFOLIO---------------------')
    sell_trades = []
    buy_trades = []
    cryptos_in_account = [crypto['Crypto'] for crypto in sorted_by_growth_cryptos]
    for crypto in sorted_by_growth_cryptos:
        quote_currency_amount = get_buy_and_sell_trades(buy_trades, crypto,
                                                        max_change_vs_portfolio, portfolio_value,
                                                        quote_currency, quote_currency_amount,
                                                        sell_trades)
    for target_crypto in TARGET_PERCENTS.keys():
        if target_crypto not in cryptos_in_account and target_crypto != quote_currency:
            funds = (TARGET_PERCENTS[target_crypto] / 100) * portfolio_value
            print(f'Funds Needed: {funds}')

            funds = min(funds, quote_currency_amount)
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


# pylint: disable-next=too-many-arguments
def get_buy_and_sell_trades(buy_trades, crypto, max_change_vs_portfolio,
                            portfolio_value, quote_currency,
                            quote_currency_amount, sell_trades):
    print(f'Crypto: {crypto["Crypto"]}, Price: {crypto["Price"]}, '
          f'Market Value: {round(crypto["MarketValue"], 2)}, '
          f'Percent: {round(crypto["CurrentPercent"], 4)}, '
          f'Target Percent: {crypto["TargetPercent"]}, '
          f'Percent Growth VS PTF = {round(crypto.get("ChangeVsPortfolio"), 4)}')
    if max_change_vs_portfolio >= REBALANCED_TARGET:
        trade, quote_currency_amount = generate_trade(crypto, quote_currency, portfolio_value,
                                                      quote_currency_amount)
        if trade:
            if trade['side'] == 'buy':
                buy_trades.append(trade)
            elif trade['side'] == 'sell':
                sell_trades.append(trade)
    return quote_currency_amount
