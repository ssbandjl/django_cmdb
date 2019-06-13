#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

# 远端服务器配置
Params = {
    "server": "47.106.101.58",
    "port": 8001,
    'url': '/assets/report/',
    'request_timeout': 30,
}

# 日志文件配置

PATH = os.path.join(os.path.dirname(os.getcwd()), 'log', 'cmdb.log') #https://www.cnblogs.com/wuxie1989/p/5623435.html


# 更多配置，请都集中在此文件中
