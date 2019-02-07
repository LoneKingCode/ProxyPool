# coding:utf-8
from urllib import request
import requests
import random
from config import HttpHeader,TIMEOUT,RETRY_TIME
from util.loghelper import LogHelper
from db.datastore import sqlhelper
from selenium import webdriver
import chardet
import config
import json
import time
import os
class WebHelper(object):
    @staticmethod
    def get_cookie(url):
        driver = webdriver.Chrome(executable_path = config.CHROME_DRIVER_PATH)
        driver.get(url)
        time.sleep(3)
        cj = driver.get_cookies()
        cookie = ''
        for c in cj:
            cookie += c['name'] + '=' + c['value'] + ';'
        driver.quit()
        return cookie

    @staticmethod
    def get_html(url,setcookie = False):
        retry_time = 0
        while retry_time < RETRY_TIME:
            try:
                headers = HttpHeader
                if setcookie:
                    headers['Cookie'] = WebHelper.get_cookie(url)
                r = requests.get(url,headers=headers,timeout=TIMEOUT )
                r.encoding = chardet.detect(r.content)['encoding']
                if (not r.ok) or len(r.content) < 500:
                    raise ConnectionError
                else:
                    return r.text

            except Exception as e:
                proxies = sqlhelper.get({'country':'国外'},10)
                if not proxies:
                    continue
                try:
                    proxy = random.choice(proxies)
                    ip = proxy['ip']
                    port = proxy['port']
                    proxies = {"http": "http://%s:%s" % (ip, port), "https":"https://%s:%s" % (ip, port)}
                    r = requests.get(url=url, headers=headers,timeout=TIMEOUT, proxies=proxies)
                    r.encoding = chardet.detect(r.content)['encoding']
                    if (not r.ok) or len(r.content) < 500:
                        raise ConnectionError
                    else:
                        return r.text
                except Exception as e:
                    pass
            time.sleep(0.5)
            retry_time +=1
        LogHelper.error('获取' + url + '内容失败')
        print('获取' + url + '内容失败')
        return None

    @staticmethod
    def proxy_valid(ip,port,return_info = False):
        proxies = {"http": "http://%s:%s" % (ip, port), "https": "https://%s:%s" % (ip, port)}
        flag,type,speed = WebHelper.check_proxy(proxies)
        _flag,_type,_speed = WebHelper.check_proxy(proxies,False)
        r_type = 0
        r_speed = 0
        r_protocol = 0
        #http
        if flag and return_info:
            r_type = type
            r_protocol = 0
            r_speed = speed
        #https
        elif _flag and return_info:
            r_type = _type
            r_protocol = 1
            r_speed = _speed
        #http_https
        elif flag and _flag and return_info:
            r_type = _type
            r_protocol = 2
            r_speed = int((speed + _speed) / 2)

        if not return_info:
            return flag or _flag
        elif return_info:
            return flag or _flag,r_type,r_protocol,r_speed

    @staticmethod
    def check_proxy(proxies,is_http = True):
        if is_http:
            test_url = config.TEST_HTTP_HEADER
        else:
            test_url = config.TEST_HTTPS_HEADER
        type = protocol = speed = 0
        start = time.time()
        try:
            response = requests.get(test_url, proxies=proxies, timeout=config.TIMEOUT)
            speed = round(time.time() - start, 2)
            if response.status_code != 200:
                return False,type,speed
            else:
                #判断什么类型，协议
                content = json.loads(response.text)
                client_ip = WebHelper.get_client_ip()
                headers = content['headers']
                ip = content['origin']
                #透明
                #例如:"origin": "42.234.9.201, 158.69.206.181"
                #还发现一个少见的情况headers中 "Forwarded": "for=本机IP:8419;by=srv-vpn:89",
                forwaded = headers.get('Forwarded','')
                if(client_ip in ip or ',' in ip or ip in forwaded):
                    type = 2
                #普通匿名 在headers中存在 "Proxy-Connection": "keep-alive" 还是暴漏了
                elif headers.get('Proxy-Connection',None):
                    type = 1
                else:
                    type = 0
                return True,type,speed

        except Exception as e:
            return False,type,speed

    @staticmethod
    def get_client_ip():
        response = requests.get(config.TEST_IP, timeout=config.TIMEOUT)
        content = json.loads(response.text)
        return content['origin']

if __name__ == '__main__':
    a = WebHelper.proxy_valid('39.135.9.103','8080')
    b = 1