import cbpro
import requests

from Config.config import CB_CREDENTIALS
from decorators.utils import timeit

def get_private_client(credentials):
    """Returns the cbpro AuthenticatedClient using the credentials from the parameters dict"""
    private_client = cbpro.AuthenticatedClient(credentials['KEY'], credentials['SECRET'], credentials['PASSPHRASE'], api_url=credentials['URL'])
    return private_client

def cbpro_private_client(func):
    def function_wrapper(*args, **kwargs):
        private_client = get_private_client(CB_CREDENTIALS)
        resp = func(private_client = private_client, *args, **kwargs)
        return resp
    return function_wrapper

def get_public_client(url):
    public_client = cbpro.PublicClient(api_url=url)
    return public_client

def cbpro_public_client(func):
    def function_wrapper(*args, **kwargs):
        public_client = get_public_client(url=CB_CREDENTIALS['URL'])
        resp = func(public_client = public_client, *args, **kwargs)
        return resp
    return function_wrapper

@timeit
@cbpro_private_client
def get_product_ticker_price(private_client, base_currency, quote_currency):
    ticker = private_client.get_product_ticker(f'{base_currency}-{quote_currency}')
    if ticker == 'NotFound':
        ticker = None
    return float(ticker['price']) or 0.0

@timeit
@cbpro_public_client
def get_products(public_client):
    products = public_client.get_products()
    return products

@timeit
@cbpro_private_client
def get_accounts(private_client):
    accounts = private_client.get_accounts()
    return accounts

@timeit
@cbpro_private_client
def place_order(private_client, product_id, side, funds):
    place_order = private_client.place_order(product_id=product_id, side=side, order_type='market', funds=funds)
    return place_order
