from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Academic_Aggregation.settings')

app = Celery('Academic_Aggregation')

# 'django.conf:settings'表示django,conf.settings也就是django项目的配置，celery会根据前面设置的环境变量自动查找并导入
# - namespace表示在settings.py中celery配置项的名字的统一前缀，这里是'CELERY_'，配置项的名字也需要大写
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))