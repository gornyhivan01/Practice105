# worker/tasks.py
import requests
from celery import Celery
import os

celery = Celery('tasks', broker=os.getenv('REDIS_URL'), backend=os.getenv('REDIS_URL'))

@celery.task(name='tasks.check_availability')
def check_availability(url):
    try:
        response = requests.get(url, timeout=10)
        return {"url": url, "status": response.status_code, "online": True}
    except:
        return {"url": url, "online": False}
