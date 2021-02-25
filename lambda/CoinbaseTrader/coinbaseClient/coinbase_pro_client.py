import cbpro


def get_private_client(credentials):
    """Returns the cbpro AuthenticatedClient using the credentials from the parameters dict"""
    private_client = cbpro.AuthenticatedClient(credentials['KEY'], credentials['SECRET'],
                                               credentials['PASSPHRASE'],
                                               api_url=credentials['URL'])
    return private_client


def get_public_client(url):
    public_client = cbpro.PublicClient(api_url=url)
    return public_client


def get_product_ticker_price(private_client, base_currency, quote_currency):
    ticker = private_client.get_product_ticker(f'{base_currency}-{quote_currency}')
    if ticker == 'NotFound':
        ticker = None
    return float(ticker['price']) or 0.0


def get_products(public_client):
    products = public_client.get_products()
    return products


def get_accounts(private_client):
    accounts = private_client.get_accounts()
    return accounts


def place_order(private_client, product_id, side, funds=None, size=None):
    if funds:
        placed_order = private_client.place_order(product_id=product_id, side=side,
                                                  order_type='market', funds=funds)
    elif size:
        placed_order = private_client.place_order(product_id=product_id, side=side,
                                                  order_type='market', size=size)
    return placed_order
