# coding:utf-8
import os
import logging
from logging import handlers

class LogHelper(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) #项目路径
    rootPath = os.path.split(BASE_DIR)[0]
    path = os.path.join(rootPath,'log')
    @staticmethod
    def debug(msg):
        Logger(os.path.join(LogHelper.path,'debug.log'), level='debug').logger.debug(msg)

    @staticmethod
    def info(msg):
        Logger(os.path.join(LogHelper.path,'info.log'), level='info').logger.info(msg)

    @staticmethod
    def warning(msg):
         Logger(os.path.join(LogHelper.path,'warning.log'),level='warning').logger.warning(msg)

    @staticmethod
    def error(msg):
        Logger(os.path.join(LogHelper.path,'error.log'), level='error').logger.error(msg)

    @staticmethod
    def critical(msg):
        Logger(os.path.join(LogHelper.path,'critical.log'), level='critical').logger.critical(msg)

class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        #sh = logging.StreamHandler()#往屏幕上输出
        #sh.setFormatter(format_str)
             ##设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位(D S M)，单位有以下几种：
        th.setFormatter(format_str)#设置文件里写入的格式
        #self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)

if __name__ == '__main__':
    LogHelper.debug('debug')
    LogHelper.error('error')
    LogHelper.warning('warning')
    LogHelper.info('info')
    LogHelper.critical('critical')