from coinbaseClient.coinbase_pro_client import get_products


def get_products_for_quote_currency_info(quote_currency):
    products = get_products()
    product_ids = []
    for product in products:
        if product['quote_currency'] != quote_currency:
            continue
        product_ids.append(product['id'])
    return product_ids
