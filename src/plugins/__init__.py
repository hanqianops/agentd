# coding: utf-8
import importlib
import platform

from conf import settings



class SysInfo(object):
    def __init__(self):
        self.plugine = settings.PLUGINS
        self.sys = platform.system()

    def collect(self):
        """动态导入采集插件"""
        server_info = {}

        for k,v in self.plugine.items():
            plugin_path,plugin = v.rsplit(".", 1)
            m = importlib.import_module(".".join([plugin_path,platform.system()]))
            func = getattr(m,plugin)
            f = func()
            server_info[k] = f.result().__dict__
        return server_info

if __name__ == '__main__':
    f = SysInfo()
    print(f.collect())

########## Windows信息格式 ##############
    """
    {
        "disk": {
            "error": null,
            "status": true,
            "data": [
                {
                    "sn": "S28ZNX0H704606",
                    "slot": 0,
                    "iface_type": "unknown",
                    "capacity": 178.85476112365723,
                    "model": "SAMSUNG MZ7LF192HCGS-000L1",
                    "manufactory": "(标准磁盘驱动器)"
                }
            ]
        },
        "os": {
            "error": null,
            "status": true,
            "data": {
                "wake_up_type": 6,
                "os_release": "10 64bit  10.0.14393 ",
                "os_distribution": "Microsoft",
                "sn": "00342-33208-03013-AAOEM",
                "asset_type": "server",
                "model": "20DFA090CD",
                "os_type": "Windows",
                "manufactory": "LENOVO"
            }
        },
        "mem": {
            "error": null,
            "status": true,
            "data": [
                {
                    "manufactory": "Samsung",
                    "slot": "ChannelA-DIMM0",
                    "model": "物理内存",
                    "sn": "50892510",
                    "capacity": 4096.0
                }
            ]
        },
        "cpu": {
            "error": null,
            "status": true,
            "data": {
                "cpu_core_count": 2,
                "cpu_count": 1,
                "cpu_model": "Intel(R) Core(TM) i3-5005U CPU @ 2.00GHz"
            }
        },
        "nic": {
            "error": null,
            "status": true,
            "data": [
                {
                    "netmask": [
                        "255.255.255.0"
                    ],
                    "name": 0,
                    "ipaddress": "10.240.250.212",
                    "macaddress": "08:00:58:00:00:01",
                    "model": "[00000000] Array Networks SSL VPN Adapter"
                },
                {
                    "netmask": [
                        "255.255.255.0",
                        "64"
                    ],
                    "name": 1,
                    "ipaddress": "192.168.71.1",
                    "macaddress": "00:50:56:C0:00:01",
                    "model": "[00000001] VMware Virtual Ethernet Adapter for VMnet1"
                },
                {
                    "netmask": [
                        "255.255.255.0",
                        "64"
                    ],
                    "name": 2,
                    "ipaddress": "192.168.100.60",
                    "macaddress": "00:50:56:C0:00:08",
                    "model": "[00000002] VMware Virtual Ethernet Adapter for VMnet8"
                },
                {
                    "netmask": "",
                    "name": 4,
                    "ipaddress": "",
                    "macaddress": "C8:5B:76:34:8E:72",
                    "model": "[00000004] Intel(R) Ethernet Connection (3) I218-V"
                },
                {
                    "netmask": [
                        "255.255.255.0",
                        "64"
                    ],
                    "name": 5,
                    "ipaddress": "192.168.199.126",
                    "macaddress": "60:6D:C7:AE:CF:6B",
                    "model": "[00000005] Broadcom 802.11ac Network Adapter"
                },
                {
                    "netmask": "",
                    "name": 7,
                    "ipaddress": "",
                    "macaddress": "62:6D:C7:AE:CF:6B",
                    "model": "[00000007] Microsoft Wi-Fi Direct Virtual Adapter"
                },
                {
                    "netmask": "",
                    "name": 18,
                    "ipaddress": "",
                    "macaddress": "48:8A:20:52:41:53",
                    "model": "[00000018] WAN Miniport (IP)"
                },
                {
                    "netmask": "",
                    "name": 19,
                    "ipaddress": "",
                    "macaddress": "72:B2:20:52:41:53",
                    "model": "[00000019] WAN Miniport (IPv6)"
                },
                {
                    "netmask": "",
                    "name": 20,
                    "ipaddress": "",
                    "macaddress": "90:DD:20:52:41:53",
                    "model": "[00000020] WAN Miniport (Network Monitor)"
                }
            ]
        }
    }
    """
