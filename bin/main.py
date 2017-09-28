# coding: utf-8
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE_DIR)

from src.plugins import SysInfo

if __name__ == '__main__':
    f = SysInfo()
    data =f.collect()
    # print(json.dumps(data, indent=4,ensure_ascii=False,))
    # print(data['os'])
    # print(data['mem'])
    # print(data['cpu'])
    # print(data['disk'])
    # print(data['nic'])
