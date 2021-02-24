from decorators.utils import timeit

def set_and_sort_crypto_change_vs_portfolio(cryptos, portfolio_value, quote_currency):
  max_change_vs_portfolio = 0
  quote_currency_amount = 0
  for crypto in cryptos:
      current_percent = (crypto["MarketValue"]/portfolio_value)*100.0
      crypto['CurrentPercent'] = current_percent
      if crypto['TargetPercent'] != 0:
          change_vs_portfolio = (current_percent/crypto['TargetPercent']*100.0) - 100.0
          crypto['ChangeVsPortfolio'] = change_vs_portfolio
          if crypto['Crypto'] == quote_currency:
              crypto['ChangeVsPortfolio'] = 0
          absolute_change = abs(change_vs_portfolio)
          if absolute_change > max_change_vs_portfolio:
              max_change_vs_portfolio = absolute_change
      else:
          crypto['ChangeVsPortfolio'] = 100
          max_change_vs_portfolio = 100
      if crypto['Crypto'] == quote_currency:
          quote_currency_amount = crypto['MarketValue']
  cryptos = sorted(cryptos, key = lambda i: i['ChangeVsPortfolio'], reverse=True)
  return cryptos, max_change_vs_portfolio, quote_currency_amount
