# coding: utf-8
__author__ = "HanQian"
__email__ = "hanqianops@163.com"

import os
import platform
import re
import subprocess
import time
import traceback

from lib.base import PluginInterface,BaseResponse
from lib.execute_cmd import shell
from lib.logger import LoggerHelper

log = LoggerHelper(__file__)


class LinuxSysInfo(PluginInterface):
    def __init__(self):
        self.ret = BaseResponse()
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
            while True:  # 检查命令是否完成
                if p.poll() == 0:
                    return p.stdout.read()
                elif wait >= timeout:
                    p.kill()
                    return ["CmdTimeOut: {0}".format(cmd)]
                else:
                    wait += 1
                    time.sleep(1)
        return p.stdout.read()

    def result(self):
        """返回采集的信息"""
        try:
            self.ret.data=self.process()
            log.run_log.info(self.ret.data)
        except Exception as e:
            msg = traceback.format_exc()
            log.error_log.error(msg)
            self.ret.status = False
            self.ret.error = msg
        return self.ret
    
    def process(self):
        """处理采集到的结果，在子类中重写该方法"""
        return NotImplemented("必须定义 process 方法")
    
    
class OsPlugin(LinuxSysInfo):
    """操作系统信息"""
    def pocess(self):
        filter_keys = ["Manufacturer", "Serial Number", "Product Name", "UUID", "Wake-up Type"]
        raw_data = {}

        for key in filter_keys:
            try:
                cmd_res = shell("dmidecode -t system|grep '%s'" % key)
                cmd_res = cmd_res.strip()

                res_to_list = cmd_res.split(":")
                if len(res_to_list) > 1:  # the second one is wanted string
                    raw_data[key] = res_to_list[1].strip()
                else:

                    raw_data[key] = -1
            except Exception as e:
                print(e)
                raw_data[key] = -2  # means cmd went wrong

        data = {"asset_type": "server"}
        data["manufactory"] = raw_data["Manufacturer"]
        data["sn"] = raw_data["Serial Number"]
        data["model"] = raw_data["Product Name"]
        data["uuid"] = raw_data["UUID"]
        data["os"] = platform.platform()
        return data

class CpuPlugin(LinuxSysInfo):
    """CPU信息"""
    def process(self):
        base_cmd = "cat /proc/cpuinfo"

        raw_data = {
            "cpu_moel": "%s |grep 'model name' |head -1 " % base_cmd,
            "cpu_count": "%s |grep  'processor'|wc -l" % base_cmd,
            "cpu_core_count": "%s |grep 'cpu cores' |awk -F: '{SUM +=$2} END {print SUM}'" % base_cmd,
        }

        for k, cmd in raw_data.items():
            cmd_res = shell(cmd)
            raw_data[k] = cmd_res.strip()

        data = {
            "cpu_count": raw_data["cpu_count"],
            "cpu_core_count": raw_data["cpu_core_count"]
        }
        cpu_model = raw_data["cpu_model"].split(":")
        if len(cpu_model) > 1:
            data["cpu_model"] = cpu_model[1].strip()
        else:
            data["cpu_model"] = -1

        return data

class NicPlugin(LinuxSysInfo):
    """网卡信息"""
    def process(self):
        raw_data = shell("ifconfig -a")
        raw_data = raw_data.split("\n")
        nic_dic = {}
        next_ip_line = False
        last_mac_addr = None
        for line in raw_data:
            if next_ip_line:
                # print last_mac_addr
                # print line #, last_mac_addr.strip()
                next_ip_line = False
                nic_name = last_mac_addr.split()[0]
                mac_addr = last_mac_addr.split("HWaddr")[1].strip()
                raw_ip_addr = line.split("inet addr:")
                raw_bcast = line.split("Bcast:")
                raw_netmask = line.split("Mask:")
                if len(raw_ip_addr) > 1:  # has addr
                    ip_addr = raw_ip_addr[1].split()[0]
                    network = raw_bcast[1].split()[0]
                    netmask = raw_netmask[1].split()[0]
                    # print(ip_addr,network,netmask)
                else:
                    ip_addr = None
                    network = None
                    netmask = None
                if mac_addr not in nic_dic:
                    nic_dic[mac_addr] = {"name": nic_name,
                                         "macaddress": mac_addr,
                                         "netmask": netmask,
                                         "network": network,
                                         "bonding": 0,
                                         "model": "unknown",
                                         "ipaddress": ip_addr,
                                         }
                else:  # mac already exist , must be boding address
                    if "%s_bonding_addr" % (mac_addr) not in nic_dic:
                        random_mac_addr = "%s_bonding_addr" % (mac_addr)
                    else:
                        random_mac_addr = "%s_bonding_addr2" % (mac_addr)

                    nic_dic[random_mac_addr] = {"name": nic_name,
                                                "macaddress": random_mac_addr,
                                                "netmask": netmask,
                                                "network": network,
                                                "bonding": 1,
                                                "model": "unknown",
                                                "ipaddress": ip_addr,
                                                }

            if "HWaddr" in line:
                # print line
                next_ip_line = True
                last_mac_addr = line

        nic_list = []
        for k, v in nic_dic.items():
            nic_list.append(v)
        return nic_list

# 输出异常， 待处理
class MemPlugin(LinuxSysInfo):
    """内存信息"""
    def process(self):
        raw_data = shell("dmidecode -t 17")
        raw_list = raw_data.split("\n")
        raw_ram_list = []
        item_list = []
        for line in raw_list:

            if line.startswith("Memory Device"):
                raw_ram_list.append(item_list)
                item_list = []
            else:
                item_list.append(line.strip())

        ram_list = []
        for item in raw_ram_list:
            item_ram_size = 0
            ram_item_to_dic = {}
            for i in item:
                # print i
                data = i.split(":")
                if len(data) == 2:
                    key, v = data

                    if key == "Size":
                        # print key ,v
                        if v.strip() != "No Module Installed":
                            ram_item_to_dic["capacity"] = v.split()[0].strip()  # e.g split "1024 MB"
                            item_ram_size = int(v.split()[0])
                            # print item_ram_size
                        else:
                            ram_item_to_dic["capacity"] = 0

                    if key == "Type":
                        ram_item_to_dic["model"] = v.strip()
                    if key == "Manufacturer":
                        ram_item_to_dic["manufactory"] = v.strip()
                    if key == "Serial Number":
                        ram_item_to_dic["sn"] = v.strip()
                    if key == "Asset Tag":
                        ram_item_to_dic["asset_tag"] = v.strip()
                    if key == "Locator":
                        ram_item_to_dic["slot"] = v.strip()

            if item_ram_size == 0:  # empty slot , need to report this
                pass
            else:
                ram_list.append(ram_item_to_dic)

        raw_total_size = shell("cat /proc/meminfo|grep MemTotal ").split(":")
        ram_data = {"ram": ram_list}
        if len(raw_total_size) == 2:  # correct

            total_mb_size = int(raw_total_size[1].split()[0]) / 1024
            ram_data["ram_size"] = total_mb_size


        return ram_data

# 输出异常， 待处理
class DiskPlugin(LinuxSysInfo):
    """磁盘信息"""
    def process(self):
        data = self.linux()
        return data

    def linux(self):
        result = {"physical_disk_driver":[]}

        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
            shell_command = "sudo %s/MegaCli  -PDList -aALL" % script_path
            output = shell(shell_command)
            result["physical_disk_driver"] = self.parse(output[1])
        except Exception as e:
            result["error"] = e
        return result

    def parse(self,content):
        """
        解析shell命令返回结果
        :param content: shell 命令结果
        :return:解析后的结果
        """
        response = []
        result = []
        for row_line in content.split("\n\n\n\n"):
            result.append(row_line)
        for item in result:
            temp_dict = {}
            for row in item.split("\n"):
                if not row.strip():
                    continue
                if len(row.split(":")) != 2:
                    continue
                key,value = row.split(":")
                name =self.mega_patter_match(key)
                if name:
                    if key == "Raw Size":
                        raw_size = re.search("(\d+\.\d+)",value.strip())
                        if raw_size:

                            temp_dict[name] = raw_size.group()
                        else:
                            raw_size = "0"
                    else:
                        temp_dict[name] = value.strip()

            if temp_dict:
                response.append(temp_dict)
        return response

    def mega_patter_match(self,needle):
        grep_pattern = {"Slot":"slot", "Raw Size":"capacity", "Inquiry":"model", "PD Type":"iface_type"}
        for key,value in grep_pattern.items():
            if needle.startswith(key):
                return value
        return False


