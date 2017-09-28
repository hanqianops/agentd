# coding: utf-8
__author__ = 'HanQian'
__email__ = 'hanqianops@163.com'

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ERROR_LOG_PATH = os.path.join(BASE_DIR,'logs/error.log')
RUN_LOG_PATH = os.path.join(BASE_DIR,'logs/run.log')

PLUGINS = {
    "disk": "src.plugins.DiskPlugin",
    "mem": "src.plugins.MemPlugin",
    "cpu": "src.plugins.CpuPlugin",
    "os": "src.plugins.OsPlugin",
    "nic": "src.plugins.NicPlugin",
}




