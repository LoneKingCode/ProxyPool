# encoding: utf-8
import sys
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__)) #项目路径
rootPath = os.path.split(BASE_DIR)[0]
sys.path.append(rootPath) #不添加的话 在其他地方执行会提示no module named
import gevent
from datetime import datetime
from multiprocessing import Queue, Process, Value
from urllib import request
from lxml import etree
from util.webhelper import WebHelper
from util.loghelper import LogHelper
from crawler.parser import Parser
import config
from validator.validator import check_proxy_from_db
from db.datastore import sqlhelper
from api.server import start_api_server
import time


proxy_set = set()
class ProxyCrawler(object):

    proxy_list = []
    last_start_datetime = datetime.now()
    finish = True
    def __init__(self,q1,q2,valid_proxy,invalid_proxy):
        self.proxy_queue = q1
        self.proxy_waitsave_queue = q2
        self.valid_proxy = valid_proxy
        self.invalid_proxy = invalid_proxy
    def run(self):
        self.first_run = True
        self.last_end_datetime = datetime.now()
        checklist = []
        while True:
            self.valid_proxy.value = 0
            self.invalid_proxy.value = 0
            now = datetime.now()
            m_diff = int((now - self.last_end_datetime).total_seconds() / 60)
            if  (m_diff >= config.CRAWL_INTERVAL and self.finish) or self.first_run:
                self.first_run = False
                self.finish = False
                proxy_set.clear()
                config.CLIENT_IP = WebHelper.get_client_ip()
                #去除数据库重复数据
                sqlhelper.deduplication()
                proxies = sqlhelper.get()
                db_proxy_num = len(proxies)
                print('>>>数据库中代理数量:%d' % db_proxy_num)

                print('>>>开始检查数据库数据')
                for p in proxies:
                    proxy_str = '%s:%s' % (p['ip'],p['port'])
                    proxy_set.add(proxy_str)
                #检查数据库中代理ip是否可用
                db_valid = Value('i',0)
                db_invalid = Value('i',0)

                checklist = []
                for proxy in proxies:
                    checklist.append(gevent.spawn(check_proxy_from_db,proxy,db_valid,db_invalid))
                    if len(checklist) >= config.CHECK_DB_TASK:
                        gevent.joinall(checklist)
                        checklist = []
                gevent.joinall(checklist)

                print('\n>>>检查数据库数据完成')
                proxies = sqlhelper.get()
                proxy_count = len(proxies)

                if proxy_count < config.DB_PROXY_MINIMUM:
                    print('>>>数据库中共 %d 条数据,小于设定数量 %d ,开始执行任务' % (proxy_count,config.DB_PROXY_MINIMUM))
                    #加入抓取网站任务
                    print('>>>开始采集网站数据')

                    crawltask = []

                    for urldata in config.UrlList:
                        crawltask.append(gevent.spawn(self.crawl,urldata))
                        if len(crawltask) >= config.CRAWL_TASK:
                            gevent.joinall(crawltask)
                            crawltask = []
                    gevent.joinall(crawltask)

                    print('>>>采集网站数据完成\n')
                    self.finish = True
                    self.last_end_datetime = datetime.now()
                else:
                    print('>>>数据库中代理数据数量已达到指定数量，本次任务不执行')
                    self.finish = True
                    self.last_end_datetime = datetime.now()
            else:
                print('>>>等待执行，下次任务执行还有 %d 分钟' % (config.CRAWL_INTERVAL - m_diff))
            time.sleep(10)

    def crawl(self,urldata):
        name = urldata['name']
        urls = urldata['urls']
        print('>>>开始分析 %s 数据,共 %d 条网址' % (name,len(urls)))
        proxy_count = 0
        proxy_list = []
        for url in urls:
            url_proxy_data = Parser.get_proxy_data(url,urldata)
            proxy_list = proxy_list + url_proxy_data
            time.sleep(1.5)             #酌情修改 有的网站限制的死
        proxy_count = len(proxy_list)
     
        success_count = exist_count = 0
        for proxy in proxy_list:
            proxy_str = '%s:%s' % (proxy['ip'],proxy['port'])
            if proxy_str not in proxy_set:
                #等待放入到队列中
                while(True):
                    if self.proxy_queue.full():
                        time.sleep(0.1)
                    else:
                        self.proxy_queue.put(proxy)
                        break
                success_count = success_count + 1
            else:
                exist_count = exist_count + 1
        print('>>>分析 %s 完成,共 %d 条代理数据,新数据 %d 条，%d 条已存在' % (name,proxy_count,success_count,exist_count))


if __name__ == '__main__':
    pass