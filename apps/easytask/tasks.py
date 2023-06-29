# -*- coding: utf-8 -*-
import time

from celery import shared_task

from .actions import update_article_cache
from .utils import TaskResponse


@shared_task
def simple_task(x, y):
    time.sleep(2)
    return x + y


@shared_task
def update_cache():
    """
    更新各种缓存
    @return:
    """
    response = TaskResponse()
    article_result = update_article_cache()
    response.data['article'] = article_result
    return response
