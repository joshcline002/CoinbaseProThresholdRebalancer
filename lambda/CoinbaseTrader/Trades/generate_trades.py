from Config.config import REBALANCE_TOLERANCE, FEE_PERCENT
from decorators.utils import timeit

def generate_trade(crypto, quote_currency, portfolio_value, quote_currency_amount):
    if crypto["Crypto"] == quote_currency:
        return None
    target_percent = crypto['TargetPercent']
    if  target_percent != 0:
        change_vs_portfolio = crypto['ChangeVsPortfolio']
        if not (abs(change_vs_portfolio) >= REBALANCE_TOLERANCE):
            return None
        if change_vs_portfolio > 0:
            side = 'sell'
        else:
            side = 'buy'
        current_percent = crypto['CurrentPercent']
        percent_difference = current_percent - target_percent
        shares = abs(round((percent_difference/current_percent)*crypto['Balance'], crypto['shares_round_to_digit']))
        quote_amount_needed = abs(round((percent_difference/100)*portfolio_value, crypto[f'{quote_currency}_round_to_digit']))
        if side == 'buy':
            if quote_amount_needed > quote_currency_amount:
                quote_amount_needed = quote_currency_amount
    else:
        side = 'sell'
        shares = crypto['Balance']
        quote_amount_needed = crypto['MarketValue']
    if shares < crypto['base_min_size'] and side == 'sell':
        return None
    elif side == 'sell':
        quote_currency_amount = quote_currency_amount + quote_amount_needed*(1-FEE_PERCENT/100)
    if quote_amount_needed < crypto['min_market_funds'] and side == 'buy':
        return None
    elif side == 'buy':
        quote_currency_amount = quote_currency_amount - quote_amount_needed
    trade = {'type': 'market',
             'side': side,
             'product_id': f'{crypto["Crypto"]}-{quote_currency}',
             'size': shares,
             'funds': quote_amount_needed
            }
    return trade
