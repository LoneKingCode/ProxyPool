import pymysql


# Mysql辅助类
class MysqlUtil(object):
    def __init__(self, config):
        #self.__create_conn()
        self.config = config
        print('mysql get config:', self.config)

    def __close(self, cursor, conn):
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        # self.__create_conn()

    def __get_conn(self):
        try:
            self.conn = pymysql.connect(host=self.config['ip'], port=self.config['port'], \
                                        user=self.config['username'], passwd=self.config['password'],
                                        db=self.config['database'], connect_timeout=self.config['connect_timeout'])
            return self.conn
        except Exception as e:
            try:
                self.conn = pymysql.connect(host=self.config['ip'], port=self.config['port'], \
                                            user=self.config['username'], passwd=self.config['password'],
                                            db=self.config['database'], connect_timeout=self.config['connect_timeout'])
                return self.conn
            except Exception as e:
                print('获取数据库连接出错:' + str(e))

    def create_db(self):
        pass

    def drop_db(self):
        pass

    def execute(self, sql):
        ids = self.execute_many([sql])
        return ids[0] if ids else None

    def execute_many(self, sqls):
        effect_row = 0
        ids = []
        try:
            conn = self.__get_conn()
            cursor = conn.cursor()
            try:
                for s in sqls:
                    effect_row += cursor.execute(s)
                    ids.append(conn.insert_id())
                conn.commit()
            except Exception as e:
                conn.rollback()
                print('执行{}出错,错误原因:{}'.format(sqls, str(e)))
            finally:
                self.__close(cursor, conn)
        except:
            pass
        return ids

    def query(self, sql, count=0):
        conn = self.__get_conn()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        result = None
        try:
            if count == 0 or not count:
                cursor.execute(sql)
                result = cursor.fetchall()
            else:
                cursor.execute(sql)
                count = int(count)
                result = cursor.fetchmany(count)
        except Exception as e:
            print('执行{}出错,错误原因:{}'.format(sql, str(e)))
        finally:
            self.__close(cursor, conn)
        return result


if __name__ == '__main__':
    pass
