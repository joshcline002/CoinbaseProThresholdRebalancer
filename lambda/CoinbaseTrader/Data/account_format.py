from Config.config import TARGET_PERCENTS, CRYPTO_EXCLUDE_FROM_TRADING, IGNORE_MARKET_VALUE_LESS_THAN
from coinbaseClient.coinbase_pro_client import get_product_ticker_price
from decorators.utils import timeit

def format_account_and_get_portfolio_value(accounts, quote_currency, products_to_quote_currency_info, private_client):
    cryptos = []
    portfolio_value = 0
    for account in accounts:
        currency = account.get('currency')
        balance = float(account.get('balance'))
        if ignore_currency(currency, balance, account):
            continue
        if currency != quote_currency:
            price = get_product_ticker_price(private_client=private_client, base_currency=currency, quote_currency=quote_currency)
        else:
            price = 1
        market_value = balance*price
        if market_value < IGNORE_MARKET_VALUE_LESS_THAN:
            continue
        product_info = get_product_info(products_to_quote_currency_info, currency, quote_currency)
        crypto = format_crypto(currency, balance, price, market_value, product_info, quote_currency)
        portfolio_value = portfolio_value + market_value
        cryptos.append(crypto)
    return cryptos, portfolio_value


def ignore_currency(currency, balance, account):
    not_in_target_and_zero_balance = currency not in TARGET_PERCENTS.keys() and balance == 0
    trading_not_enabled = not account.get('trading_enabled')
    exclude_crypto = currency in CRYPTO_EXCLUDE_FROM_TRADING
    return not_in_target_and_zero_balance or trading_not_enabled or exclude_crypto

def format_crypto(currency, balance, price, market_value, product_info, quote_currency):
    formatted_crypto = {
        'Crypto': currency,
        'Balance': balance,
        'Price': price,
        'MarketValue': market_value,
        'TargetPercent': TARGET_PERCENTS.get(currency) or 0.0,
        'base_min_size': float(product_info['base_min_size']),
        'base_max_size': float(product_info['base_max_size']),
        'min_market_funds': float(product_info['min_market_funds']),
        'max_market_funds': float(product_info['max_market_funds']),
        f'{quote_currency}_round_to_digit': product_info[f'{quote_currency}_round_to_digit'],
        'shares_round_to_digit': product_info['shares_round_to_digit']
    }
    return formatted_crypto

def get_product_info(products_to_quote_currency_info, currency, quote_currency):
    product = products_to_quote_currency_info.get(currency) \
     or {'base_min_size': '0.0', 'base_max_size': '0.0',
         'min_market_funds': '0.0', 'max_market_funds': '0.0',
         f'{quote_currency}_round_to_digit': 2, 'shares_round_to_digit': 0}
    return product
