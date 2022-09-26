# encoding: utf-8
from lxml import etree
import re
from config import UrlList
from util.loghelper import LogHelper
from util.WebUtil import WebUtil
import html


# 转换器
class Parser(object):
    @staticmethod
    # 分析获取代理数据
    def get_proxy_data(url, urldata):
        type = urldata['type']
        proxylist = []
        try:

            if type == 'xpath':
                proxylist = Parser.xpath_parser(url, urldata)
            elif type == 'regular':
                proxylist = Parser.regular_parser(url, urldata)
            elif type == 'custom':
                proxylist = Parser.custom_parser(url, urldata)
            else:
                print('网址配置错误，请填写正确的type')
                LogHelper.error('网址配置错误，请填写正确的type,url:' + url)
            print('url:{} type:{} 获取数据数:{}'.format(url, type, len(proxylist)))
            return proxylist
        except Exception as e:
            LogHelper.error('转换失败,URL:' + url + ' 错误信息:' + str(e))
            return proxylist

    @staticmethod
    def xpath_parser(url, urldata):
        is_secret_cookie = 'cookie' in urldata.keys() and urldata['cookie'] == 'secret_cookie'
        html = WebUtil.get_html(url, is_secret_cookie)
        proxylist = []
        if not html:
            return proxylist
        html = etree.HTML(html, parser=etree.HTMLParser(encoding='utf-8'))
        proxy_data = html.xpath(urldata['pattern'])

        for proxy in proxy_data:
            ip = proxy.xpath(urldata['position']['ip'])[0].text.strip()
            port = proxy.xpath(urldata['position']['port'])[0].text.strip()
            proxy_type = ''
            protocol = ''
            if urldata['position']['type'] != '':
                proxy_type = proxy.xpath(urldata['position']['type'])[0].text.strip()
            else:
                proxy_type = '高匿'
            if urldata['position']['protocol'] != '':
                protocol = proxy.xpath(urldata['position']['protocol'])[0].text.strip()
            else:
                protocol = 'http'
            try:
                proxylist.append({'ip': ip, 'port': int(port), 'type': proxy_type, 'protocol': protocol})
            except:
                continue
        return proxylist

    @staticmethod
    def regular_parser(url, urldata):
        content = WebUtil.get_html(url)
        proxylist = []
        if not content:
            return proxylist
        content = html.escape(content)
        proxy_data = re.findall(urldata['pattern'], content, re.S)
        ip = ''
        port = ''
        proxy_type = ''
        protocol = ''
        if urldata['position']['ip'] == '':
            return
        if urldata['position']['port'] == '':
            return
        for proxy in proxy_data:
            ip = proxy[int(urldata['position']['ip'])]
            port = proxy[int(urldata['position']['port'])]
            if urldata['position']['type'] != '':
                proxy_type = proxy[int(urldata['position']['type'])]
            if urldata['position']['protocol'] != '':
                protocol = proxy[int(urldata['position']['protocol'])]
            proxylist.append({'ip': ip, 'port': int(port), 'type': proxy_type, 'protocol': protocol})
        return proxylist

    @staticmethod
    def custom_parser(url, urldata):
        proxylist = []
        try:
            modulename = urldata['methodname']
            parser = __import__('crawler.parser', fromlist=('ParserExtension', ))
            parser_ext = getattr(parser, 'ParserExtension')
            func = getattr(parser_ext, modulename)
            proxylist = func(urldata)
        except Exception as e:
            LogHelper.error('未找到指定的转换模块:%s 或转换出错:%s' % (modulename, str(e)))
        return proxylist


class ParserExtension(object):
    def goubanjia(urldata):
        html = WebUtil.get_html(urldata['urls'][0])
        html = etree.HTML(html)
        proxy_data = html.xpath('//table/tbody/tr[position()>=1]')
        ipAndPort_xpath = './td[1]'
        type_xpath = './td[2]'
        protocol_xpath = './td[3]'
        proxylist = []
        for data in proxy_data:
            ip = ''
            port = 0
            type = data.xpath('./td[2]/a/text()')[0]
            protocol = data.xpath('./td[3]/a/text()')[0]

            ip_port_data = data.xpath(ipAndPort_xpath)[0]
            for e in ip_port_data:
                e_style = e.attrib['style'] if 'style' in e.attrib.keys() else ''
                e_class = e.attrib['class'] if 'class' in e.attrib.keys() else ''

                if 'port' in e_class:
                    if e.text:
                        b = e_class.split(' ')[1]
                        c = []
                        for x in b:
                            c.append(x)
                        d = len(c)
                        f = []
                        for g in range(0, d):
                            f.append(str('ABCDEFGHIZ'.index(c[g])))
                        port = int(''.join(f)) >> 0x3
                elif 'none' not in e_style or e_style == '':
                    if e.text:
                        ip += e.text

            proxylist.append({'ip': ip, 'port': int(port), 'type': type, 'protocol': protocol})

        return proxylist


if __name__ == '__main__':
    a = Parser.get_proxy_data('http://www.89ip.cn/tqdl.html?api=1&num=9999&port=&address=&isp=', UrlList[2])
