import os
import random

# 项目路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# API服务器IP
API_SERVER_IP = '0.0.0.0'
# API服务器端口
API_SERVER_PORT = 8000

# 网址采集规则
# xpath，regular：正则表达式，custom：自定义方法，在crawler.parser.ParserExtension中定义
# cookie参数 secret_cookie (有些网站通过第一次访问时返回JS代码来生成新的cookie 之后都需要带上这个cookie访问
# 不然就返回521错误)
UrlList = [
    # {
    #     'name': '云代理',
    #     'urls': ['http://www.ip3366.net/free/?stype=%s&page=%s' % (t, p) for t in range(1, 2) for p in range(1, 2)],
    #     'type': 'xpath',
    #     'pattern': '//*[@id="list"]/table/tbody/tr[position()>1]',
    #     'position': {
    #         'ip': './td[1]',
    #         'port': './td[2]',
    #         'type': '',
    #         'protocol': '',
    #     },
    # },
    {
        'name': '云代理',
        'urls': ['http://www.ip3366.net/free/?stype=%s&page=%s' % (t, p) for t in range(1, 3) for p in range(1, 8)],
        'type': 'xpath',
        'pattern': '//*[@id="list"]/table/tbody/tr[position()>1]',
        'position': {
            'ip': './td[1]',
            'port': './td[2]',
            'type': '',
            'protocol': '',
        },
    },
    {
        'name': '开心代理',
        'urls': ['http://www.kxdaili.com/dailiip/%s/%s.html' % (t, i) for t in range(1, 3) for i in range(1, 11)],
        'type': 'xpath',
        'pattern': '//table//tr[position()>1]',
        'position': {
            'ip': './td[1]',
            'port': './td[2]',
            'type': './td[3]',
            'protocol': './td[4]',
        }
    },
    {
        'name': '89免费代理',
        'urls': ['http://www.89ip.cn/tqdl.html?api=1&num=9999&port=&address=&isp='],
        'type': 'regular',
        'pattern': '([0-9]+.[0-9]+.[0-9]+.[0-9]+):([0-9]+)',
        'position': {
            'ip': 0,
            'port': 1,
            'type': '',
            'protocol': '',
        },
    },
    {
        'name': '66免费代理网',
        #选取每个地区的前五页数据 33页已经是不存在的了
        'urls': ['http://www.66ip.cn/areaindex_%s/%s.html' % (n, i) for n in range(1, 34) for i in range(1, 6)] + ['http://www.66ip.cn/%s.html' % i for i in range(1, 6)],
        'type': 'xpath',
        'pattern': "//*[@id=‘footer’]/div/table/tbody/tr[position()>1]",
        'position': {
            'ip': './td[1]',
            'port': './td[2]',
            'type': './td[4]',
            'protocol': '',
        },
        'protocol': '',
        'cookie': 'secret_cookie'
    },
    {
        'name': '快代理',
        'urls': ['http://www.kuaidaili.com/free/%s/%s/' % (m, n) for m in ['inha', 'intr'] for n in range(1, 5)],
        'type': 'xpath',
        'pattern': ".//*[@id='list']/table/tbody/tr[position()>0]",
        'position': {
            'ip': './td[1]',
            'port': './td[2]',
            'type': './td[3]',
            'protocol': './td[4]'
        }
    }
    ##国内访问不了 代理数量1W+ 但是获取有问题 提示需要执行js 而且5秒后才跳转
    # {
    #     'name':'hidemy',
    #     'urls': ['https://hidemy.name/en/proxy-list/%s#list' % n for n in
    #     ([''] + ['?start=%s' % (64 * m) for m in range(1, 3)])],
    #     'type': 'xpath',
    #     'pattern': ".//table[@class ='proxy__t']/tbody/tr",
    #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': '',
    #     'protocol': ''}
    # },
]

# sqlite数据库文件位置
# DATABASE_PATH = os.path.join(BASE_DIR, 'data/proxy.db')
# 数据库连接配置
DATABASE_CONFIG = {
    'ip': '127.0.0.1',
    'port': 3306,
    'username': 'root',
    'password': '123456',
    'database': 'proxypool',
}
# 纯真IP数据文件位置
QQWRY_PATH = os.path.join(BASE_DIR, 'data/qqwry.dat')

# 数据库中最低代理数量 低于这个数量会执行任务开始采集
DB_PROXY_MINIMUM = 3000
# 抓取间隔 每隔时间会检测是否需要进行采集任务 *单位分钟
CRAWL_INTERVAL = 60
# 检查数据库中数据有效性及更新数据线程数
CHECK_DB_TASK = 50
# 同时进行几个网站的采集任务
CRAWL_TASK = 5
# 检查数据有效性及存储的线程数
CHECK_SAVE_PROXY_THREAD = 10
# 验证代理连接超时
TIMEOUT = 10
# 爬虫抓取网页数据重试次数
RETRY_TIME = 3

# 获取本机IP
TEST_IP = 'http://httpbin.org/ip'
# 检测代理类型和是否可用
TEST_HTTP_HEADER = 'http://httpbin.org/get'
TEST_HTTPS_HEADER = 'https://httpbin.org/get'
# 本机IP 无需配置，程序每次执行任务都会更新它 为检测代理类型使用
CLIENT_IP = '0.0.0.0'
# USER_AGENTS 随机信息
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
]

# HTTP头
HttpHeader = {
    'User-Agent': random.choice(USER_AGENTS),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate',
    'Cookie': ''
}
