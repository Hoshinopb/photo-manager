"""
Celery 配置文件

使用 Redis 作为消息代理和结果后端
"""
import os
from celery import Celery

# 设置 Django 配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 创建 Celery 应用
app = Celery('photo_manager')

# 从 Django 配置中加载 Celery 配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现各 app 中的 tasks.py
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
