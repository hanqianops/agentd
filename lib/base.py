# coding: utf-8
__author__ = 'HanQian'
__email__ = 'hanqianops@163.com'

import abc

class BaseResponse(object):
    def __init__(self):
        """格式化返回信息"""
        self.status = True
        self.data = None
        self.error = None


class PluginInterface(metaclass=abc.ABCMeta):
    """采集插件接口"""

    @abc.abstractmethod
    def result(self):
        pass



