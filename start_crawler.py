from gevent import monkey

monkey.patch_all()

from multiprocessing import Queue, Value
from validator.validator import allocate_check_task
from db.datastore import data_store
from crawler.proxycrawler import ProxyCrawler
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

if __name__ == '__main__':
    threadPool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="crawler_")

    proxy_queue = Queue()  # 抓取网站后保存的代理数据
    proxy_waitsave_queue = Queue()  # 等待验证入库的数据
    # 记录抓取任务的有效 无效代理数
    valid_proxy = Value('i', 0)
    invalid_proxy = Value('i', 0)
    crawler = ProxyCrawler(proxy_queue, proxy_waitsave_queue, valid_proxy, invalid_proxy)
    # 开始抓取数据并放入已抓取队列
    t1 = threadPool.submit(crawler.run)
    # 分配 验证已抓取代理并放入待存储队列 的任务
    t2 = threadPool.submit(allocate_check_task, args=(proxy_queue, proxy_waitsave_queue, valid_proxy, invalid_proxy))
    # 从存储队列中取数据并入库
    t3 = threadPool.submit(data_store)
    wait([t1, t2, t3], return_when=ALL_COMPLETED)
