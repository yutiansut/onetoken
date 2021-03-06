import asyncio
import logging
import os

import aiohttp
import onetoken as ot
import yaml
from onetoken import Account, log, util

demo_args = {
    'OT_KEY': '',
    'OT_SECRET': '',
    'account': 'huobip/mock-demo',
    'contract': 'huobip/btc.usdt',
}


def load_api_key_secret():
    path = os.path.expanduser('~/.onetoken/config.yml')
    if os.path.isfile(path):
        try:
            js = yaml.load(open(path).read())
            if 'ot_key' in js:
                return js['ot_key'], js['ot_secret'], js['account']
            return js['api_key'], js['api_secret'], js['account']
        except:
            log.exception('failed load api key/secret')
    return None, None, None


async def main():
    ot_key, ot_secret, account = load_api_key_secret()
    if ot_key is None or ot_secret is None:
        file_path = '~/.onetoken/config.yml'
        try:
            config = yaml.load(open(os.path.expanduser(file_path)).read())
            if 'ot_key' in config:
                ot_key = config['ot_key']
                ot_secret = config['ot_secret']
                account = config['account']
            else:
                ot_key = config['api_key']
                ot_secret = config['api_secret']
                account = config['account']
        except:
            print('file not found: ', os.path.expanduser(file_path))
            print('input manually:')
            ot_key = input('ot-key: ')
            ot_secret = input('ot-secret: ')
            account = input('account: ')
    acc = Account(account, ot_key, ot_secret)
    log.info('Initialized account {}'.format(account))

    # 获取账号 info
    info, err = await acc.get_info()
    if err:
        log.warning('Get info failed.', err)
    else:
        log.info(f'Account info: {info.data}')

    # 根据 pos_symbol 获取账号持仓数量
    # 现货类似 btc, bch
    # 期货类似 btc.usd.q
    pos_symbol = 'btc'
    amount = info.get_total_amount(pos_symbol)
    log.info(f'Amount: {amount} {pos_symbol}')

    contract_symbol_1 = 'huobip/btc.usdt'
    contract_symbol_2 = 'huobip/eth.usdt'

    # 下单
    order_1, err = await acc.place_order(con=contract_symbol_1, price=20000, bs='s', amount=0.01)
    if err:
        log.warning('Place order failed.', err)
    else:
        log.info(f'New order: {order_1}')

    client_oid = util.rand_client_oid(contract_symbol_2)  # client oid 为预设下单 id，方便策略后期跟踪
    log.info(f'Random client_oid: {client_oid}')

    order_2, err = await acc.place_order(con=contract_symbol_2, price=10000, bs='s', amount=1.3, client_oid=client_oid)
    if err:
        log.warning('Place order failed.', err)
    else:
        log.info(f'New order: {order_2}')

    # 根据contract和state获取订单列表, 此处获取的是active状态的订单列表
    o_list, err = await acc.get_order_list(contract=contract_symbol_1, state='active')
    if err:
        log.warning('Get active order list failed.', err)
    else:
        log.info(f'Active order list: {o_list}')

    # 用get_pending_list方法可以更快捷地获取active状态的订单列表
    p_list, err = await acc.get_pending_list(contract=contract_symbol_2)
    if err:
        log.warning('Get pending list failed.', err)
    else:
        log.info(f'Pending list: {p_list}')

    exchange_oid_1 = order_1['exchange_oid']
    exchange_oid_2 = order_2['exchange_oid']

    # 通过exchange_oid获取order_1的订单详情
    o_info_1, err = await acc.get_order_use_exchange_oid(exchange_oid_1)
    if err:
        log.warning('Get order info by exchange_oid failed.', err)
    else:
        log.info(f'Order info by exchange_oid: {o_info_1}')

    # 可以输入多个exchange_oid并且用逗号分割,以实现批量查询
    o_info_bulk, err = await acc.get_order_use_exchange_oid(','.join([exchange_oid_1, exchange_oid_2]))
    if err:
        log.warning('Get order info by exchange_oid failed.', err)
    else:
        log.info(f'Order info by exchange_oid: {o_info_bulk}')

    # 通过client_oid获取order_2的订单详情
    o_info_2, err = await acc.get_order_use_client_oid(client_oid)
    if err:
        log.warning('Get order info by client_oid failed.', err)
    else:
        log.info(f'Order info by client_oid: {o_info_2}')

    # 通过exchange_oid撤单
    res, err = await acc.cancel_use_exchange_oid(exchange_oid_1)
    if err:
        log.warning('Cancel order by exchange_oid failed.', err)
    else:
        log.info(f'Canceled order by exchange_oid: {res}')

    # 通过client_oid撤单
    res, err = await acc.cancel_use_client_oid(client_oid)
    if err:
        log.warning('Cancel order by client_oid failed.', err)
    else:
        log.info(f'Canceled order by client_oid: {res}')

    # 根据contract和state获取历史订单列表
    o_list, err = await acc.get_order_list(contract=contract_symbol_1, state='end')
    if err:
        log.warning('Get order history failed.', err)
    else:
        log.info(f'Order history: {o_list}')
    o_list, err = await acc.get_order_list(contract=contract_symbol_2, state='end')
    if err:
        log.warning('Get order history failed.', err)
    else:
        log.info(f'Order history: {o_list}')

    # 继续下单
    order_more, err = await acc.place_order(con=contract_symbol_1, price=20000, bs='s', amount=0.1)
    if err:
        log.warning('Place order failed.', err)
    else:
        log.info(f'New order: {order_more}')

    # 下单收到返回后撤单
    res, err = await acc.place_and_cancel(con=contract_symbol_1, price=20000, bs='s', amount=0.01, sleep=2)
    if err:
        log.warning('Place and cancel order failed.', err)
    else:
        log.info(f'Place and cancel order result: {res}')

    # 撤掉指定contract的所有订单
    res, err = await acc.cancel_all(contract=contract_symbol_1)
    if err:
        log.warning('Cancel all orders failed.', err)
    else:
        log.info(f'Cancel all orders result: {res}')

    acc.close()


if __name__ == '__main__':
    ot.log_level(logging.INFO)
    print('ots folder', ot)
    print('ots version', ot.__version__)
    print('aiohttp version', aiohttp.__version__)
    asyncio.get_event_loop().run_until_complete(main())
