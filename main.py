from coinbaseClient.coinbase_pro_client import get_products, get_accounts, get_product_ticker, get_prices, place_order
from Config.config import TARGET_PERCENTS, CRYPTO_EXCLUDE_FROM_TRADING, REBALANCE_TARGET, REBALANCE_TOLERANCE, IGNORE_MARKET_VALUE_LESS_THAN, FEE_PERCENT, ENABLE_TRADING
import datetime



def main():
    print(f'--------START TIME {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-----------')
    products = get_products()

    products_to_usd_info = {}

    for product in products:
        if product['quote_currency'] != 'USD':
            continue
        products_to_usd_info[product['base_currency']] ={
                'base_min_size': float(product['base_min_size']),
                'base_max_size': float(product['base_max_size']),
                'min_market_funds': float(product['min_market_funds']),
                'max_market_funds': float(product['max_market_funds']),
                'usd_round_to_digit': len(product['quote_increment'].split('.')[-1].rstrip('0')),
                'shares_round_to_digit': len(product['base_increment'].split('.')[-1].rstrip('0'))
            }
    accounts = get_accounts()
    cryptos = []
    portfolio_value = 0
    for account in accounts:
        currency = account.get('currency')
        balance = float(account.get('balance'))
        if (currency not in TARGET_PERCENTS.keys() and balance == 0) or not account.get('trading_enabled') or currency in CRYPTO_EXCLUDE_FROM_TRADING:
            continue
        if currency != 'USD':
            price = float(get_product_ticker(currency=currency).get('price') or 0.0)
        else:
            price = 1
        market_value = balance*price
        if market_value < IGNORE_MARKET_VALUE_LESS_THAN:
            continue
        product_info = products_to_usd_info.get(currency) \
         or {'base_min_size': '0.0', 'base_max_size': '0.0',
             'min_market_funds': '0.0', 'max_market_funds': '0.0',
             'usd_round_to_digit': 2, 'shares_round_to_digit': 0}
        crypto = {
            'Crypto': currency,
            'Balance': balance,
            'Price': price,
            'MarketValue': market_value,
            'TargetPercent': TARGET_PERCENTS.get(currency) or 0.0,
            'base_min_size': float(product_info['base_min_size']),
            'base_max_size': float(product_info['base_max_size']),
            'min_market_funds': float(product_info['min_market_funds']),
            'max_market_funds': float(product_info['max_market_funds']),
            'usd_round_to_digit': product_info['usd_round_to_digit'],
            'shares_round_to_digit': product_info['shares_round_to_digit']
        }
        portfolio_value = portfolio_value + market_value
        cryptos.append(crypto)
    max_change_vs_portfolio = 0
    for crypto in cryptos:
        current_percent = (crypto["MarketValue"]/portfolio_value)*100
        crypto['CurrentPercent'] = current_percent
        if crypto['TargetPercent'] != 0:
            change_vs_portfolio = (current_percent/crypto['TargetPercent']*100) - 100
            crypto['ChangeVsPortfolio'] = change_vs_portfolio
            absolute_change = abs(change_vs_portfolio)
            if absolute_change > max_change_vs_portfolio:
                max_change_vs_portfolio = absolute_change
        else:
            crypto['ChangeVsPortfolio'] = 0
    cryptos = sorted(cryptos, key = lambda i: i['ChangeVsPortfolio'], reverse=True)

    sell_trades = []
    buy_trades = []
    cash_amount = 0
    for crypto in cryptos:
        if crypto['Crypto'] == 'USD':
            cash_amount = crypto['MarketValue']
    print('------------------STATS---------------------')
    print(f"Target Percent: {REBALANCE_TARGET}, Tolerance: {REBALANCE_TOLERANCE}, Portfolio Value: {portfolio_value}, Max Change: {max_change_vs_portfolio}, Cash: {cash_amount}")
    print('------------------PORTFOLIO---------------------')
    for crypto in cryptos:
        print(f'Crypto: {crypto["Crypto"]}, Market Value: {crypto["MarketValue"]}, Percent: {crypto["CurrentPercent"]}, Target Percent: {crypto["TargetPercent"]}, Percent Growth VS PTF = {crypto.get("ChangeVsPortfolio")}')
    if max_change_vs_portfolio >= REBALANCE_TARGET:
        for crypto in cryptos:
            if crypto["Crypto"] == 'USD':
                continue
            target_percent = crypto['TargetPercent']
            if  target_percent != 0:
                change_vs_portfolio = crypto['ChangeVsPortfolio']
                if not (abs(change_vs_portfolio) >= REBALANCE_TOLERANCE):
                    continue
                if change_vs_portfolio > 0:
                    side = 'sell'
                else:
                    side = 'buy'
                current_percent = crypto['CurrentPercent']
                percent_difference = current_percent - target_percent
                shares = abs(round((percent_difference/current_percent)*crypto['Balance'], crypto['shares_round_to_digit']))
                usd_amount = abs(round((percent_difference/100)*portfolio_value, crypto['usd_round_to_digit']))
                if side == 'buy':
                    if usd_amount > cash_amount:
                        usd_amount = cash_amount
            else:
                side = 'sell'
                shares = crypto['Balance']
                usd_amount = crypto['MarketValue']
            if shares < crypto['base_min_size'] and side == 'sell':
                continue
            elif side == 'sell':
                cash_amount = cash_amount + usd_amount*(1-FEE_PERCENT/100)
            if usd_amount < crypto['min_market_funds'] and side == 'buy':
                continue
            elif side == 'buy':
                cash_amount = cash_amount - usd_amount
            trade = {'type': 'market',
                     'side': side,
                     'product_id': f'{crypto["Crypto"]}-USD',
                     'size': shares,
                     'funds': usd_amount
                    }
            if side == 'buy':
                buy_trades.append(trade)
            elif side == 'sell':
                sell_trades.append(trade)

    if ENABLE_TRADING:
        trade_title = 'TRADES EXECUTED'
    else:
        trade_title = 'TRADES TO EXECUTE'
    print(f'------------------{trade_title}---------------------')
    buy_trades.reverse()
    if len(buy_trades) > 0 or len(sell_trades) > 0:
        for trade in sell_trades:
            print(trade)
            if ENABLE_TRADING:
                response = place_order(side=trade['side'], product_id=trade['product_id'], funds=trade['funds'])
        for trade in buy_trades:
            print(trade)
            if ENABLE_TRADING:
                response = place_order(side=trade['side'], product_id=trade['product_id'], funds=trade['funds'])
    else:
        print(f"No asset exceeding {REBALANCE_TARGET} no trades needed.")



    print(f"Ending Cash: {cash_amount}")
    print(f'--------END TIME {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-----------')
main()
