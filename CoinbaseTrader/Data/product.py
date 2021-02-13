from coinbaseClient.coinbase_pro_client import get_products


def get_products_for_quote_currency_info(quote_currency):
    products = get_products()
    products_to_quote_currency_info = {}

    for product in products:
        if product['quote_currency'] != quote_currency:
            continue
        products_to_quote_currency_info[product['base_currency']] ={
                'base_min_size': float(product['base_min_size']),
                'base_max_size': float(product['base_max_size']),
                'min_market_funds': float(product['min_market_funds']),
                'max_market_funds': float(product['max_market_funds']),
                f'{quote_currency}_round_to_digit': len(product['quote_increment'].split('.')[-1].rstrip('0')),
                'shares_round_to_digit': len(product['base_increment'].split('.')[-1].rstrip('0'))
            }
    return products_to_quote_currency_info
