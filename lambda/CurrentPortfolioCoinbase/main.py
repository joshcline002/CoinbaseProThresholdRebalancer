import boto3
import csv
import io
from datetime import date as get_date

from coinbaseClient.coinbase_pro_client import get_accounts
from Config.config import CRYPTO_EXCLUDE_FROM_TRADING, BUCKET_NAME

s3 = boto3.client('s3')


def main(event, context):
    accounts = get_accounts()
    csv_io = io.StringIO()
    writer = csv.writer(csv_io)
    writer.writerow(['date', 'currency', 'balance'])
    current_date = get_date.today()
    for account in accounts:
        if float(account['balance']) < 0.0008 or not account['trading_enabled'] \
                or account['currency'] in CRYPTO_EXCLUDE_FROM_TRADING:
            continue
        writer.writerow([current_date, account['currency'], account['balance']])
    file_key = f'coinbase_pro_accounts/yyyy={current_date.year}/mm={current_date.month}/dd={current_date.day}/' \
               f'{current_date}-coinbase-account-balance.csv'
    s3.put_object(Body=csv_io.getvalue(), ContentType='text/csv', Bucket=BUCKET_NAME,
                  Key=file_key)
    csv_io.close()
