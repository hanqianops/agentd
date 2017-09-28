# coding: utf-8
__author__ = 'HanQian'
__email__ = 'hanqianops@163.com'

import platform
import traceback

import win32com
import wmi

from lib.base import PluginInterface, BaseResponse
from lib.logger import LoggerHelper
log = LoggerHelper(__file__)

class WinSysInfo(PluginInterface):
    """windows系统的插件基类"""
    def __init__(self):
        self.wmi_obj = wmi.WMI()
        self.wmi_service_obj = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector =self.wmi_service_obj.ConnectServer(".","root\cimv2")
        self.ret = BaseResponse()

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


class CpuPlugin(WinSysInfo):
    """CPU信息"""
    def process(self):
        data = {}
        cpu_lists = self.wmi_obj.Win32_Processor()
        cpu_core_count = 0

        for cpu in cpu_lists:
            cpu_core_count += cpu.NumberOfCores
            cpu_model = cpu.Name
        data["cpu_count"] = len(cpu_lists)
        data["cpu_model"] = cpu_model
        data["cpu_core_count"] =cpu_core_count
        return data

class DiskPlugin(WinSysInfo):
    """磁盘信息"""
    # def result(self):
    #     try:
    #         self.ret.data=self.process()
    #         log.run_log.info(self.ret.data)
    #     except Exception as e:
    #         msg = traceback.format_exc()
    #         log.error_log.error(msg)
    #         self.ret.status = False
    #         self.ret.error = msg
    #     return self.ret

    def process(self):
        data = []
        for disk in self.wmi_obj.Win32_DiskDrive():
            #print  disk.Model,disk.Size,disk.DeviceID,disk.Name,disk.Index,disk.SerialNumber,disk.SystemName,disk.Description
            item_data = {}
            iface_choices = ["SAS","SCSI","SATA","SSD"]
            for iface in iface_choices:
                if iface in disk.Model:
                    item_data['iface_type']  = iface
                    break
            else:
                item_data['iface_type']  = 'unknown'
            item_data['slot']  = disk.Index
            item_data['sn']  = disk.SerialNumber
            item_data['model']  = disk.Model
            item_data['manufactory']  = disk.Manufacturer
            item_data['capacity']  = int(disk.Size ) / (1024*1024*1024)
            data.append(item_data)
        return data

class MemPlugin(WinSysInfo):
    """内存信息"""
    # def result(self):
    #     try:
    #         self.ret.data=self.process()
    #         log.run_log.info(self.ret.data)
    #     except Exception as e:
    #         msg = traceback.format_exc()
    #         log.error_log.error(msg)
    #         self.ret.status = False
    #         self.ret.error = msg
    #     return self.ret

    def process(self):
        data = []
        ram_collections = self.wmi_service_connector.ExecQuery("Select * from Win32_PhysicalMemory")
        for item in ram_collections:
            item_data = {}
            mb = int(1024 * 1024)
            ram_size = int(item.Capacity) / mb
            item_data = {
                "slot":item.DeviceLocator.strip(),
                "capacity":ram_size,
                "model":item.Caption,
                "manufactory":item.Manufacturer,
                "sn":item.SerialNumber,
            }
            data.append(item_data)

        return data

class OsPlugin(WinSysInfo):
    """系统信息"""
    # def result(self):
    #     try:
    #         self.ret.data=self.process()
    #         log.run_log.info(self.ret.data)
    #     except Exception as e:
    #         msg = traceback.format_exc()
    #         log.error_log.error(msg)
    #         self.ret.status = False
    #         self.ret.error = msg
    #     return self.ret

    def process(self):
        data = {
            'os_type': platform.system(),
            'os_release': "%s %s  %s " % (platform.release(), platform.architecture()[0], platform.version()),
            'asset_type': 'server'
        }

        computer_info =  self.wmi_obj.Win32_ComputerSystem()[0]
        system_info =  self.wmi_obj.Win32_OperatingSystem()[0]
        data['manufactory'] = computer_info.Manufacturer
        data['model'] = computer_info.Model
        data['wake_up_type'] = computer_info.WakeUpType
        data['sn'] = system_info.SerialNumber

        return data

class NicPlugin(WinSysInfo):
    """网卡信息"""
    # def result(self):
    #     try:
    #         self.ret.data=self.process()
    #         log.run_log.info(self.ret.data)
    #     except Exception as e:
    #         msg = traceback.format_exc()
    #         log.error_log.error(msg)
    #         self.ret.status = False
    #         self.ret.error = msg
    #     return self.ret

    def process(self):
        data = []
        for nic in self.wmi_obj.Win32_NetworkAdapterConfiguration():
            if nic.MACAddress is not None:
                item_data = {}
                item_data['macaddress'] = nic.MACAddress
                item_data['model'] = nic.Caption
                item_data['name'] = nic.Index
                if nic.IPAddress  is not None:
                    item_data['ipaddress'] = nic.IPAddress[0]
                    item_data['netmask'] = nic.IPSubnet
                else:
                    item_data['ipaddress'] = ''
                    item_data['netmask'] = ''
                bonding = 0
                data.append(item_data)

        return data

