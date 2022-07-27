import sys
from unittest.mock import MagicMock

sys.modules['coinbase_client'] = MagicMock()
sys.modules['coinbase_client.my_coinbase_pro_client'] = MagicMock()

# pylint: disable-next=import-error, wrong-import-position
from data import product


def test_get_precision_of_decimal_float():
    actual_precision = product.get_precision_of_decimal("1.99")
    expected_precision = 2
    assert actual_precision == expected_precision


def test_get_precision_of_decimal_int():
    actual_precision = product.get_precision_of_decimal("1")
    expected_precision = 0
    assert actual_precision == expected_precision


def test_get_products_for_quote_currency_info():
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

    product.get_products = MagicMock(return_value=products)
    product.get_precision_of_decimal = MagicMock(return_value="Test_Precision")
    actual_products = product.get_products_for_quote_currency_info('USD', 'Public_Client')
    expected_products = {'BTC':
                             {'base_min_size': .001,
                              'base_max_size': 1000.0,
                              'min_market_funds': .1,
                              'max_market_funds': 1000.0,
                              'USD_round_to_digit': "Test_Precision",
                              'shares_round_to_digit': "Test_Precision"
                              },
                         'ETH':
                             {'base_min_size': 1.0,
                              'base_max_size': 1000.0,
                              'min_market_funds': 1.0,
                              'max_market_funds': 1000.0,
                              'USD_round_to_digit': "Test_Precision",
                              'shares_round_to_digit': "Test_Precision"
                              }
                         }
    assert actual_products == expected_products
    product.get_products.assert_called_once_with('Public_Client')
