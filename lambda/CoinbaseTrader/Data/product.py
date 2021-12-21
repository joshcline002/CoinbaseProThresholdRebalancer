from coinbaseClient.coinbase_pro_client import get_products


def get_products_for_quote_currency_info(quote_currency, public_client):
    products = get_products(public_client)
    products_to_quote_currency_info = {}
    for product in products:
        if product['quote_currency'] != quote_currency:
            continue
        products_to_quote_currency_info[product['base_currency']] = {
            'base_min_size': float(product['base_min_size']),
            'base_max_size': float(product['base_max_size']),
            'min_market_funds': float(product['min_market_funds']),
            'max_market_funds': float(product['max_market_funds']),
            f'{quote_currency}_round_to_digit': get_precision_of_decimal(
                product['quote_increment']),
            'shares_round_to_digit': get_precision_of_decimal(product['base_increment'])
        }
    return products_to_quote_currency_info


def get_precision_of_decimal(decimal_num):
    if '.' not in decimal_num:
        return 0
    split_on_zero = decimal_num.split('.')
    get_numbers_after_decimal = split_on_zero[-1]
    removed_trailing_zeros = get_numbers_after_decimal.rstrip('0')
    precision = len(removed_trailing_zeros)
    return precision
