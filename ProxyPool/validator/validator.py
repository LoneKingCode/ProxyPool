# coding:utf-8
import json
import os
import gevent
from db.datastore import sqlhelper
from db.sqlhelper import ProxyType,ProxyProtocol
from util.webhelper import WebHelper
from util.loghelper import LogHelper
import time
import requests
from datetime import datetime
import config
from util.IpLocater import IpLocater
from multiprocessing import Queue,Process
import threading
import sys
import psutil

def check_proxy_from_db(proxy,db_valid,db_invalid):
        ip = proxy['ip']
        port = proxy['port']
        score = int(proxy['score'])
        #检测代理ip是否可用 并更新下速度，协议和类型
        proxy_str = '%s:%s' % (ip,port)
        flag,type,protocol,speed = WebHelper.proxy_valid(ip,port,True)
        if flag:
            #print('数据库中 %s 有效√' % proxy_str)
            db_valid.value = db_valid.value + 1
            iplocater = IpLocater()
            ipaddr = iplocater.getIpAddr(iplocater.str2ip(ip))
            if(iplocater.isDomestic(ipaddr)):
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
            row_affect = sqlhelper.update(proxy,{'ip':ip,'port':port})

        else:
            #print('数据库中 %s 无效×' % proxy_str)
            db_invalid.value = db_invalid.value + 1
            #分数减到0时就移除
            if score <= 1:
                sqlhelper.delete({'ip':ip,'port':port})
            else:
                sqlhelper.update({'score':score - 1,'checkdatetime':str(datetime.now())},{'ip':ip,'port':port})

        info = '\r>>>数据库中{0}有效,{1}无效\r'.format(db_valid.value,db_invalid.value)
        sys.stdout.write(info)
        sys.stdout.flush()
def allocate_check_task(proxy_queue,proxy_waitsave_queue,valid_proxy,invalid_proxy):
    taskprocess = Queue()
    p_check_count = 0
    tasklist = []
    wait_time = 0
    while True:
        wait_time = wait_time + 1
        if wait_time > 3:
            #print('分配检查代理并放入待存储队列任务......')
            if(len(tasklist) > 0):
                threading.Thread(target=start_check_proxy_wait_save,args=(tasklist,proxy_waitsave_queue,taskprocess,valid_proxy,invalid_proxy)).start()
                wait_time = 0

        while not proxy_queue.empty():
            tasklist.append(proxy_queue.get()) 
            while((len(tasklist) >= config.PROCESS_CHECK_SAVE_PROXY)):
                #print('分配检查代理并放入待存储队列任务......')
                threading.Thread(target=start_check_proxy_wait_save,args=(tasklist,proxy_waitsave_queue,taskprocess,valid_proxy,invalid_proxy)).start()
                wait_time = 0
                tasklist.clear()
        time.sleep(15)
    #while True:
    #    if not taskprocess.empty():
    #        try:
    #            pid = taskprocess.get()
    #            ps = psutil.Process(pid)
    #            ps.kill()
    #            p_check_count = p_check_count - 1
    #            #print('杀死子进程:' + str(pid))
    #        except Exception as e:
    #            p_check_count = p_check_count - 1

    #    wait_time = wait_time + 1
    #    if wait_time > 3 and tasklist:
    #        p_check_proxy =
    #        Process(target=start_check_proxy_wait_save,args=(tasklist,proxy_waitsave_queue,taskprocess,valid_proxy,invalid_proxy))
    #        p_check_proxy.start()
    #        p_check_count = p_check_count + 1
    #        tasklist.clear()
    #        wait_time = 0

    #    while not proxy_queue.empty():
    #        tasklist.append(proxy_queue.get())
    #        #每个进程去验证并保存多少条代理
    #        while((len(tasklist) >= config.PROCESS_CHECK_SAVE_PROXY)) and
    #        p_check_count < config.  PROCESS_CHECK_MAX:
    #            #print('分配检查代理并放入待存储队列任务......')
    #            p_check_proxy =
    #            Process(target=start_check_proxy_wait_save,args=(tasklist,proxy_waitsave_queue,taskprocess,valid_proxy,invalid_proxy))
    #            p_check_proxy.start()
    #            p_check_count = p_check_count + 1
    #            tasklist.clear()
    #            wait_time = 0
    #    time.sleep(15)
def start_check_proxy_wait_save(tasklist,proxy_waitsave_queue,taskprocess,valid_proxy,invalid_proxy):
        print('分配检查任务完成，开始执行任务......')
        checklist = []
        for proxy in tasklist:
            checklist.append(gevent.spawn(check_proxy_wait_save, proxy,proxy_waitsave_queue,valid_proxy,invalid_proxy))
        gevent.joinall(checklist)
        #taskprocess.put(os.getpid())
        #print('任务执行完成......')

#检测代理是否可用 可用放入队列等待入库
def check_proxy_wait_save(proxy,proxy_waitsave_queue,valid_proxy,invalid_proxy):
    ip = proxy['ip']
    port = proxy['port']
    flag,type,protocol,speed = WebHelper.proxy_valid(ip,port,True)
    if flag:
        valid_proxy.value = valid_proxy.value + 1
        #print('%s:%s 有效√ 等待入库' % (proxy['ip'],proxy['port']))

        country = '国内'
        area = '北京'
        iplocater = IpLocater()
        ipaddr = iplocater.getIpAddr(iplocater.str2ip(ip))
        if('省' in ipaddr or iplocater.isDomestic(ipaddr)):
            country = '国内'
            area = ipaddr
        else:
            country = '国外'
            area = ipaddr
        model = {'ip':ip,'port':port,'speed':speed,'type':type,'protocol':protocol,'country':country,'area':area,'score':10,'checkdatetime':str(datetime.now())}
        #等待放入到代存储队列中
        proxy_waitsave_queue.put(model)
    else:
        invalid_proxy.value = invalid_proxy.value + 1
    info = '\r>>>%d条有效,%d条无效,等待入库\r' % (valid_proxy.value,invalid_proxy.value)
    sys.stdout.write(info)
    sys.stdout.flush()
if __name__ == '__main__':
    pass