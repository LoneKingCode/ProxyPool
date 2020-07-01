from gevent import monkey

monkey.patch_all()

from multiprocessing import Queue, Process, Value
from ProxyPool.validator.validator import allocate_check_task
from ProxyPool.db.datastore import data_store
from ProxyPool.api.server import start_api_server
from ProxyPool.crawler.proxycrawler import ProxyCrawler

if __name__ == '__main__':
    proxy_queue = Queue()  # 抓取网站后保存的代理数据
    proxy_waitsave_queue = Queue()  # 等待验证入库的数据
    # 记录抓取任务的有效 无效代理数
    valid_proxy = Value('i', 0)
    invalid_proxy = Value('i', 0)
    crawler = ProxyCrawler(proxy_queue, proxy_waitsave_queue, valid_proxy, invalid_proxy)

    # 开始抓取数据并放入已抓取队列
    p0 = Process(target=crawler.run)

    # 分配 验证已抓取代理并放入待存储队列 的任务
    p1 = Process(target=allocate_check_task, args=(proxy_queue, proxy_waitsave_queue, valid_proxy, invalid_proxy))

    # 从存储队列中取数据并入库
    p2 = Process(target=data_store, args=(proxy_waitsave_queue,))

    # 开启api服务器
    p3 = Process(target=start_api_server)

    p3.start()
    p0.start()
    p1.start()
    p2.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
