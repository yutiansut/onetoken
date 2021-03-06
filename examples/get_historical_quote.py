"""
使用方法

git clone https://github.com/1token-trade/onetoken
cd onetoken
python examples/get_historical_quote.py
"""
import random

import requests
import gzip
import json


def get_contracts(date):
    url = 'http://alihz-net-0.qbtrade.org/contracts?date={}'.format(date)
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        print('fail get contracts', r.status_code, r.text)
    print('----------available contracts------------')
    print('total size', len(r.json()))
    print('first 10 contracts', r.json()[:10])


def download(contract, date):
    url = 'http://alihz-net-0.qbtrade.org/hist-ticks?date={}&contract={}'.format(date, contract)
    print('downloading', url)
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        print('fail get historical tick', r.status_code, r.text)
        return
    block_size = 300 * 1024
    total = 0
    with open('examples/tick-{}-{}.gz'.format(date, contract.replace('/', '-')), 'wb') as f:
        for data in r.iter_content(block_size):
            f.write(data)
            total += len(data) / 1024
            print('{} {} downloaded {}kb'.format(contract, date, round(total)))


def unzip_and_read(path):
    data = open(path, 'rb').read()
    r = gzip.decompress(data).decode()
    total = len(r.splitlines())
    print('total', total, 'ticks')
    print('--------this script will print randomly ticks--------------')
    for i, line in enumerate(r.splitlines()):
        try:
            tick = json.loads(line)
            if random.random() < 0.0001:
                print('{}/{}'.format(i, total), tick)
        except:
            pass


def main():
    date = '2018-02-02'
    get_contracts(date)

    download('huobip/btc.usdt', '2018-02-02')  # this file size is around 15MB

    unzip_and_read('examples/tick-2018-02-02-huobip-btc.usdt.gz')


if __name__ == '__main__':
    main()
