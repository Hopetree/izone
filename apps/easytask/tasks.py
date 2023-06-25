from celery import shared_task
import time


@shared_task
def simple_task(x, y):
    time.sleep(5)
    return x + y
