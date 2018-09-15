# -*- coding: utf-8 -*-
# @File : main.py
# @Author : Xie
# @Date   : 9/10/18
# @Desc   : 启动worker的入口


# 为celery使用django配置文件进行设置(单独设置,临时)
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):  # getenv 如果Django的app系统未设置环境变量,那么就主动配置
    os.environ['DJANGO_SETTINGS_MODULE'] = 'buyfree_mall.settings.dev'

from celery import Celery

# 创建celery应用
celery_app = Celery('buyfree')
# 导入celery配置
celery_app.config_from_object('celery_tasks.config')

# 自动发现celery任务(列表) 默认会调用sms包内的 task.py文件,所以不用写 task.py
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])

