#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform
import win32com
import wmi

"""
本模块基于windows操作系统，依赖wmi和win32com库，需要提前使用pip进行安装，windows中没有方便的命令可以获取硬件信息，但是有额外的模块可以帮助我们实现目的，这个模块叫做wmi
或者下载安装包手动安装(见pywin32-220.win-amd64-py3.5(配合wmi模块，获取主机信息的模块).exe)。
"""


def collect():
    data = {
        'os_type': platform.system(),
        'os_release': "%s %s  %s " % (platform.release(), platform.architecture()[0], platform.version()),
        'os_distribution': 'Microsoft',
        'asset_type': 'server'
    }

    # 分别获取各种硬件信息
    win32obj = Win32Info()
    data.update(win32obj.get_cpu_info())
    data.update(win32obj.get_ram_info())
    data.update(win32obj.get_motherboard_info())
    data.update(win32obj.get_disk_info())
    data.update(win32obj.get_nic_info())
    # 最后返回一个数据字典
    return data


class Win32Info(object):

    def __init__(self):
        # 固定用法，更多内容请参考模块说明
        self.wmi_obj = wmi.WMI()
        self.wmi_service_obj = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector = self.wmi_service_obj.ConnectServer(".", "root\cimv2")

    def get_cpu_info(self):
        """
        获取CPU的相关数据，这里只采集了三个数据，实际有更多，请自行选择需要的数据
        :return:
        """
        data = {}
        cpu_lists = self.wmi_obj.Win32_Processor()
        cpu_core_count = 0
        for cpu in cpu_lists:
            cpu_core_count += cpu.NumberOfCores

        cpu_model = cpu_lists[0].Name   # CPU型号（所有的CPU型号都是一样的）
        data["cpu_count"] = len(cpu_lists)      # CPU个数
        data["cpu_model"] = cpu_model
        data["cpu_core_count"] = cpu_core_count  # CPU总的核数

        return data

    def get_ram_info(self):
        """
        收集内存信息
        :return:
        """
        data = []
        # 这个模块用SQL语言获取数据
        ram_collections = self.wmi_service_connector.ExecQuery("Select * from Win32_PhysicalMemory")
        for item in ram_collections:    # 主机中存在很多根内存，要循环所有的内存数据
            ram_size = int(int(item.Capacity) / (1024**3))  # 转换内存单位为GB
            item_data = {
                "slot": item.DeviceLocator.strip(),
                "capacity": ram_size,
                "model": item.Caption,
                "manufacturer": item.Manufacturer,
                "sn": item. SerialNumber,
            }
            data.append(item_data)  # 将每条内存的信息，添加到一个列表里

        return {"ram": data}    # 再对data列表封装一层，返回一个字典，方便上级方法的调用

    def get_motherboard_info(self):
        """
        获取主板信息
        :return:
        """
        computer_info = self.wmi_obj.Win32_ComputerSystem()[0]
        system_info = self.wmi_obj.Win32_OperatingSystem()[0]
        data = dict()
        data['manufacturer'] = computer_info.Manufacturer
        data['model'] = computer_info.Model
        data['wake_up_type'] = computer_info.WakeUpType
        data['sn'] = system_info.SerialNumber
        return data

    def get_disk_info(self):
        """
        硬盘信息
        :return:
        """
        data = []
        for disk in self.wmi_obj.Win32_DiskDrive():     # 每块硬盘都要获取相应信息
            item_data = dict()
            iface_choices = ["SAS", "SCSI", "SATA", "SSD"]
            for iface in iface_choices:
                if iface in disk.Model:
                    item_data['iface_type'] = iface
                    break
            else:
                item_data['iface_type'] = 'unknown'
            item_data['slot'] = disk.Index
            item_data['sn'] = disk.SerialNumber
            item_data['model'] = disk.Model
            item_data['manufacturer'] = disk.Manufacturer
            item_data['capacity'] = int(int(disk.Size) / (1024**3))
            data.append(item_data)

        return {'physical_disk_driver': data}

    def get_nic_info(self):
        """
        网卡信息
        :return:
        """
        data = []
        for nic in self.wmi_obj.Win32_NetworkAdapterConfiguration():
            if nic.MACAddress is not None:
                item_data = dict()
                item_data['mac'] = nic.MACAddress
                item_data['model'] = nic.Caption
                item_data['name'] = nic.Index
                if nic.IPAddress is not None:
                    item_data['ip_address'] = nic.IPAddress[0]
                    item_data['net_mask'] = nic.IPSubnet
                else:
                    item_data['ip_address'] = ''
                    item_data['net_mask'] = ''
                data.append(item_data)

        return {'nic': data}

if __name__ == "__main__":
    # 测试代码
    dic = collect()
    print(dic)

# DEMO DATA 单独运行一下该脚本（注意不是运行CMDB项目），查看一下生成的数据。为了显示更直观，可以通过在线json校验工具格式化一下。
# {
# os_type': 'Windows',
# 'os_release': '764bit6.1.7601',
# 'os_distribution': 'Microsoft',
# 'asset_type': 'server',
# 'cpu_count': 1,
# 'cpu_model': 'Intel(R)Core(TM)i5-2300CPU@2.80GHz',
# 'cpu_core_count': 4,
# 'ram': [
#     {
#         'slot': 'A0',
#         'capacity': 4,
#         'model': 'PhysicalMemory',
#         'manufacturer': '',
#         'sn': ''
#     },
#     {
#         'slot': 'A1',
#         'capacity': 4,
#         'model': 'PhysicalMemory',
#         'manufacturer': '',
#         'sn': ''
#     }
# ],
# 'manufacturer': 'GigabyteTechnologyCo.,
# Ltd.',
# 'model': 'P67X-UD3R-B3',
# 'wake_up_type': 6,
# 'sn': '00426-OEM-8992662-12006',
# 'physical_disk_driver': [
#     {
#         'iface_type': 'unknown',
#         'slot': 0,
#         'sn': '3830414130423230233235362020202020202020',
#         'model': 'KINGSTONSV100S264GATADevice',
#         'manufacturer': '(标准磁盘驱动器)',
#         'capacity': 59
#     },
#     {
#         'iface_type': 'unknown',
#         'slot': 1,
#         'sn': '2020202020202020201020205935334445414235',
#         'model': 'ST2000DL003-9VT166ATADevice',
#         'manufacturer': '(标准磁盘驱动器)',
#         'capacity': 1863
#     }
# ],
# 'nic': [
#     {
#         'mac': '24: CF: 92: FF: 48: 34',
#         'model': '[
#             00000011
#         ]RealtekRTL8192CUWirelessLAN802.11nUSB2.0NetworkAdapter',
#         'name': 11,
#         'ip_address': '192.168.1.100',
#         'net_mask': ('255.255.255.0',
#         '64')
#     },
#     {
#         'mac': '0A: 00: 27: 00: 00: 00',
#         'model': '[
#             00000013
#         ]VirtualBoxHost-OnlyEthernetAdapter',
#         'name': 13,
#         'ip_address': '192.168.56.1',
#         'net_mask': ('255.255.255.0',
#         '64')
#     },
#     {
#         'mac': '24: CF: 92: FF: 48: 34',
#         'model': '[
#             00000017
#         ]MicrosoftVirtualWiFiMiniportAdapter',
#         'name': 17,
#         'ip_address': '',
#         'net_mask': ''
#     },
#     {
#         'mac': '10: 19: 86: 00: 12: 98',
#         'model': '[
#             00000018
#         ]Bluetooth设备(个人区域网)',
#         'name': 18,
#         'ip_address': '',
#         'net_mask': ''
#     }
# ]
# }
#
#
