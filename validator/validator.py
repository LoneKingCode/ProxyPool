# coding:utf-8
import sys
import threading
import time
from datetime import datetime
from multiprocessing import Queue

import gevent

import config
from db.datastore import sqlhelper
from util.IpLocater import IpLocater
from util.WebUtil import WebUtil
from concurrent.futures import ThreadPoolExecutor

threadPool = ThreadPoolExecutor(max_workers=config.CHECK_SAVE_PROXY_THREAD, thread_name_prefix="validator_")


def check_proxy_from_db(proxy, db_valid, db_invalid):
    ip = proxy['ip']
    port = proxy['port']
    score = int(proxy['score'])
    # 检测代理ip是否可用 并更新下速度，协议和类型
    flag, type, protocol, speed = WebUtil.proxy_valid(ip, port, True)
    if flag:
        db_valid.value = db_valid.value + 1
        iplocater = IpLocater()
        ipaddr = iplocater.getIpAddr(iplocater.str2ip(ip))
        if (iplocater.isDomestic(ipaddr)):
            country = '国内'
            area = ipaddr
        else:
            country = '国外'
            area = ipaddr
        proxy['checkdatetime'] = str(datetime.now())
        proxy['type'] = type
        proxy['protocol'] = protocol
        proxy['speed'] = speed
        proxy['score'] = score + 1
        proxy['country'] = country
        proxy['area'] = area
        proxy.pop('id')
        row_affect = sqlhelper.update(proxy, {'ip': ip, 'port': port})

    else:
        # print('数据库中 %s 无效×' % proxy_str)
        db_invalid.value = db_invalid.value + 1
        # 分数减到0时就移除
        if score <= 1:
            sqlhelper.delete({'ip': ip, 'port': port})
        else:
            sqlhelper.update({'score': score - 1, 'checkdatetime': str(datetime.now())}, {'ip': ip, 'port': port})

    info = '\r>>>数据库中{0}有效,{1}无效\r'.format(db_valid.value, db_invalid.value)
    sys.stdout.write(info)
    sys.stdout.flush()


def allocate_check_task(proxy_queue, proxy_waitsave_queue, valid_proxy, invalid_proxy):
    tasklist = []
    wait_time = 0
    while True:
        wait_time = wait_time + 1
        # 防止任务量过少 等待过久不执行
        if wait_time > 3:
            # print('分配检查代理并放入待存储队列任务......')
            if len(tasklist) > 0:
                start_check_proxy_wait_save(tasklist, proxy_waitsave_queue, valid_proxy, invalid_proxy)
                wait_time = 0

        while not proxy_queue.empty():
            tasklist.append(proxy_queue.get())
            while len(tasklist) >= config.CHECK_SAVE_PROXY_THREAD:
                # print('分配检查代理并放入待存储队列任务......')
                start_check_proxy_wait_save(tasklist, proxy_waitsave_queue, valid_proxy, invalid_proxy)
                wait_time = 0
                tasklist.clear()
        time.sleep(15)


def start_check_proxy_wait_save(tasklist, proxy_waitsave_queue, valid_proxy, invalid_proxy):
    # print('分配检查任务完成，开始执行任务......')
    for proxy in tasklist:
        threadPool.submit(check_proxy_wait_save, args=(proxy, proxy_waitsave_queue, valid_proxy, invalid_proxy))
        #threading.Thread(target=check_proxy_wait_save, args=(proxy, proxy_waitsave_queue, valid_proxy, invalid_proxy)).start()


# 检测代理是否可用 可用放入队列等待入库
def check_proxy_wait_save(proxy, proxy_waitsave_queue, valid_proxy, invalid_proxy):
    ip = proxy['ip']
    port = proxy['port']
    flag, type, protocol, speed = WebUtil.proxy_valid(ip, port, True)
    if flag:
        valid_proxy.value = valid_proxy.value + 1
        # print('%s:%s 有效√ 等待入库' % (proxy['ip'],proxy['port']))

        country = '国内'
        area = '北京'
        iplocater = IpLocater()
        ipaddr = iplocater.getIpAddr(iplocater.str2ip(ip))
        if ('省' in ipaddr or iplocater.isDomestic(ipaddr)):
            country = '国内'
            area = ipaddr
        else:
            country = '国外'
            area = ipaddr
        model = {'ip': ip, 'port': port, 'speed': speed, 'type': type, 'protocol': protocol, 'country': country, 'area': area, 'score': 10, 'checkdatetime': str(datetime.now())}
        # 等待放入到代存储队列中
        proxy_waitsave_queue.put(model)
    else:
        invalid_proxy.value = invalid_proxy.value + 1
    # info = '\r>>>%d条有效,%d条无效,等待入库\r' % (valid_proxy.value, invalid_proxy.value)
    info = '\r>>>%d条有效,%d条无效\r' % (valid_proxy.value, invalid_proxy.value)
    sys.stdout.write(info)
    sys.stdout.flush()


if __name__ == '__main__':
    pass
