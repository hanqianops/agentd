# coding: utf-8
__author__ = 'HanQian'
__email__ = 'hanqianops@163.com'

import subprocess
import time


def shell(cmd, timeout=None):
    """
    执行命令
    :param timeout: 命令超时时间
    :return: list
    """
    wait = 0
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True, shell=True)

    if timeout:
        while True:      # 检查命令是否完成
            if p.poll() == 0:
                return p.stdout.read()
            elif wait >= timeout:
                p.kill()
                return ["CmdTimeOut: {0}".format(cmd)]
            else:
                wait += 1
                time.sleep(1)
    return p.stdout.read()

