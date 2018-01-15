# coding: utf-8
__author__ = 'HanQian'
__email__ = 'hanqianops@163.com'
# coding: utf-8

import logging
from conf import settings

class LoggerHelper(object):
    """
    记录日志

    调用方式：
        f = LoggerHelper(__file__)
        f.error_log(50,message)
    """
    _i = None
    def __new__(cls, *args, **kwargs):
        """单例模式, 对象只能创建一次"""
        if not cls._i:
            cls._i = object.__new__(cls)
        return cls._i

    def __init__(self, logger_name):
        # 程序运行日志
        run_log = logging.Logger(logger_name, level=logging.INFO)
        file = logging.FileHandler(settings.RUN_LOG_PATH, 'a+', encoding='utf-8')
        fmt = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")
        file.setFormatter(fmt)
        run_log.addHandler(file)

        # 程序错误日志
        error_log = logging.Logger(logger_name, level=logging.INFO)
        file = logging.FileHandler(settings.ERROR_LOG_PATH, 'a+', encoding='utf-8')
        fmt = logging.Formatter(fmt="%(asctime)s - %(levelname)s - "
                                    "[%(name)s:%(funcName)s:%(lineno)d] : %(message)s")
        file.setFormatter(fmt)
        error_log.addHandler(file)

        self.error_log = error_log
        self.run_log = run_log
