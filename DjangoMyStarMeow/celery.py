#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Version :   Ver1.0
@Author  :   LR
@License :   (C) Copyright 2013-2017, MyStudy
@Contact :   xyliurui@look
@Software:   PyCharm
@File    :   celery.py
@Time    :   2018/7/3 13:21
@Desc    :
"""

# >pip install celery
from __future__ import absolute_import  # 从 future 模块导入 absolute_import，这样，celery.py 模块就不会与 Celery 库相冲突
from celery import Celery
import os
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoMyStarMeow.settings")
# 为 celery 命令行程序设置环境变量 DJANGO_SETTINGS_MODULE 的默认值
# 设置这个环境变量是为了让 celery 命令能找到 Django 项目。这条语句必须出现在 Celery 实例创建之前

broker = 'redis://127.0.0.1:6379/6'  # 将要进行的任务
backend = 'redis://127.0.0.1:6379/7' # 返回的结果
# 创建celery应用,Project名字
app = Celery('DjangoMyStarMeow', broker=broker, backend=backend)
app.config_from_object('django.conf:settings', namespace='CELERY')
# 将 Django settings 模块作为 Celery 的配置来源。也就是说，不需要使用多个配置文件，直接在 Django settings 里面配置 Celery.
# 可以将 settings 对象作为参数传入，但是更好的方式是使用字符串，因为当使用 Windows 系统或者 execv 时 celery worker 不需要序列化 settings 对象
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# 为了重用 Django APP，通常是在单独的 tasks.py 模块中定义所有任务。Celery 会自动发现这些模块


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# celery -A DjangoMyStarMeow worker --pool=solo -l info
