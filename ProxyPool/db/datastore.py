from db.sqlhelper import SqlHelper
import time
import datetime
sqlhelper = SqlHelper()

#保存代理数据到数据库中
def data_store(proxy_waitsave_queue):
        while True:
            time.sleep(20)
            if not proxy_waitsave_queue.empty():
                print('>>>开始入库，本次待入库 %d 条数据' % proxy_waitsave_queue.qsize())
            count = 0
            models = []
            while not proxy_waitsave_queue.empty():
                proxy = proxy_waitsave_queue.get()
                models.append(proxy)
            if len(models) > 0:
                row_affect = sqlhelper.add(models)
                retrytime = 1
                while row_affect <= 0 and retrytime <= 3:
                    print('>>>入库失败，再次执行...第%d次' % row_affect)
                    row_affect = sqlhelper.add(models)
                    retrytime = retrytime + 1
                    time.sleep(1)
                print('>>>入库完成，本次共入库 %d 条数据' % row_affect)
