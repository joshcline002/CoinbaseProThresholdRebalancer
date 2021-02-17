import boto3
import csv
import io
from datetime import date as get_date
from coinbaseClient.coinbase_pro_client import get_product_ticker_price

from Data.product import get_products_for_quote_currency_info
from Config.config import BUCKET_NAME

s3 = boto3.client('s3')


def main():
    quote_currency = 'USD'
    products_to_quote_currency_info = get_products_for_quote_currency_info(quote_currency)
    print(products_to_quote_currency_info)

    csv_io = io.StringIO()
    writer = csv.writer(csv_io)
    writer.writerow(['date', 'baseCurrency', 'quoteCurrency', 'price'])
    current_date = get_date.today()
    for product_id in products_to_quote_currency_info:
        price = get_product_ticker_price(product_id=product_id)
        curr = product_id.split('-')
        writer.writerow([current_date, curr[0], curr[1], price])
    file_key = f'coinbase_pro_prices/yyyy={current_date.year}/mm={current_date.month}/' \
               f'dd={current_date.day}/{current_date}-coinbase-prices.csv'
    s3.put_object(Body=csv_io.getvalue(), ContentType='text/csv', Bucket=BUCKET_NAME,
                  Key=file_key)
    csv_io.close()


main()
