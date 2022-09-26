import queue
import sqlite3


def singleton(cls):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class SqliteHelper(object):
    __queue_conn = queue.Queue(maxsize=1)
    __path = ''

    def __init__(self):
        self.__path = path
        self.__create_conn()

    def __create_conn(self):
        conn = sqlite3.connect(self.__path, check_same_thread=False)
        self.__queue_conn.put(conn)

    def __close(self, cursor, conn):
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close  # cursor.close()
        self.__create_conn()

    def query(self, sql, params):
        conn = self.__queue_conn.get()
        cursor = conn.cursor()
        value = None
        try:
            records = None
            if not params is None:
                records = cursor.execute(sql, params).fetchall()
            else:
                records = cursor.execute(sql).fetchall()
            field = [i[0] for i in cursor.description]
            value = [dict(zip(field, i)) for i in records]
        finally:
            self.__close(cursor, conn)
            return value

    def execute(self, sql):
        conn = self.__queue_conn.get()
        cursor = conn.cursor()
        try:
            cursor.executescript(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self.__close(cursor, conn)

    def update(self, sql, params):
        return self.execute_update_many([sql], [params])

    def update_many(self, sql_list, params_list):
        conn = self.__queue_conn.get()
        cursor = conn.cursor()
        count = 0
        try:
            for index in range(len(sql_list)):
                sql = sql_list[index]
                params = params_list[index]
                if not params is None:
                    count += cursor.execute(sql, params).rowcount
                else:
                    count += cursor.execute(sql).rowcount
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self.__close(cursor, conn)
        return count


# example:

# one = SQLiteUtil('xxx.sqlite')

# rst = one.execute_query('select * from website', None)
# for line in rst:
# print(line.get('id'), line.get('url'), line.get('content'))

# print(one.execute_update('update website set content = \'2222222\' where id = ?', ('1',)))
# print(one.execute_update('update website set content = \'2222222\' where id = \'1\'', None))

# print('update many')
# count = one.execute_update_many(
# [
# 'update website set content = \'一\' where id = \'1\'',
# 'update website set content = \'二\' where id = \'2\'',
# 'update website set content = 1 where id = \'3\''
# ],
# [None, None, None]
# )
# print('count:', count)

# 去重复
# ('DELETE FROM Proxy_Main \
#    WHERE rowid IN \
#   (SELECT p.rowid \
#    FROM Proxy_Main p \
#    INNER JOIN \
#         (SELECT ip, port, MIN(rowid) As min_id \
#          FROM Proxy_Main \
#          GROUP BY ip, port \
#          HAVING COUNT(*) > 1) AS agg \
#    ON p.ip = agg.ip AND p.port = agg.port \
#    AND p.rowid <> agg.min_id);')

if __name__ == '__main__':
    one = SqliteHelper(DATABASE_PATH)
    rst = one.execute_update('update Proxy_Main set score=score+1 where ip=\'36.89.180.87\'', None)
    print(rst)
