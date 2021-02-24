from unittest.mock import MagicMock
import sys
from ....CoinbaseTrader.Data import product

def test_get_products_for_quote_currency_info():
    cbpro_client = sys.modules['coinbaseClient.coinbase_pro_client']
    products = [
                {'quote_currency': 'USD',
                 'base_currency': 'BTC',
                 'base_min_size': '.001',
                 'base_max_size': '1000',
                 'min_market_funds': '.1',
                 'max_market_funds': '1000',
                 'quote_increment': '.00100',
                 'base_increment': '.00000100000'
                },
                {'quote_currency': 'USD',
                 'base_currency': 'ETH',
                 'base_min_size': '1',
                 'base_max_size': '1000',
                 'min_market_funds': '1',
                 'max_market_funds': '1000',
                 'quote_increment': '1',
                 'base_increment': '1'
                },
                {'quote_currency': 'EUR',
                 'base_currency': 'BTC',
                 'base_min_size': '.001',
                 'base_max_size': '1000',
                 'min_market_funds': '.1',
                 'max_market_funds': '1000',
                 'quote_increment': '.00100',
                 'base_increment': '.00000100000'
                }]
    get_products = MagicMock(return_value = products)

    actual_products = product.get_products_for_quote_currency_info('USD')
    expected_products = {'BTC':
                            {'base_min_size': .001,
                             'base_max_size': 1000,
                             'min_market_funds': .1,
                             'max_market_funds': 1000,
                             'USD_round_to_digit': 3,
                             'shares_round_to_digit': 6
                            },
                        'ETH':
                            {'base_min_size': 1,
                             'base_max_size': 1000,
                             'min_market_funds': 1,
                             'max_market_funds': 1000,
                             'USD_round_to_digit': 0,
                             'shares_round_to_digit': 0
                            }
                         }
    assert actual_products == expected_products
