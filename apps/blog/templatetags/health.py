import json
import logging
from datetime import datetime, timedelta
from django import template
from django.core.cache import cache

from blog.utils import RedisKeys
from blog.models import Fitness

logger = logging.getLogger(__name__)
register = template.Library()


def time_to_seconds(time_str):
    # 分割时间字符串
    minutes, seconds = map(int, time_str.split(':'))
    # 转换为秒
    total_seconds = minutes * 60 + seconds
    return total_seconds


def time_to_minutes(time_str):
    # 分割时间字符串，得到分钟和秒
    minutes, seconds = map(int, time_str.split(':'))
    # 将秒转换为分钟，并加上分钟部分
    total_minutes = minutes + seconds / 60
    return f'{total_minutes:.1f}'


@register.simple_tag
def get_year_data():
    """
    获取当年所有跑步数据，日历图
    @return:
    """
    this_date_str = datetime.today().strftime('%Y%m%d')
    this_year = datetime.today().year
    redis_key = RedisKeys.health_year_data.format(date=this_date_str)
    redis_data = cache.get(redis_key)
    if redis_data:
        return redis_data
    data = {}
    rawData = []
    objs = Fitness.objects.filter(run_date__year=this_year)
    for obj in objs:
        run_date = obj.run_date.strftime('%Y-%m-%d')
        distance = obj.distance * 1000
        rawData.append([run_date, distance])
    data['rawData'] = rawData
    data['year'] = this_year
    # print(data)
    cache.set(redis_key, data, 3600 * 2)
    return data


@register.simple_tag
def get_heart_rate_interval(num=14):
    """
    获取心率区间分布
    @param num: 获取最新num条数据
    @return:
    """
    this_date_str = datetime.today().strftime('%Y%m%d')
    redis_key = RedisKeys.heart_rate_interval.format(date=this_date_str)
    redis_key = f'{redis_key}_{num}'
    redis_data = cache.get(redis_key)
    if redis_data:
        return redis_data
    data = {}
    objs = Fitness.objects.order_by('-run_date')[:num]
    objs = list(objs)[::-1]
    tData = []
    xData = []
    for obj in objs:
        xData.append(obj.run_date.strftime('%m-%d'))
        heart_rate_interval = [time_to_seconds(t) for t in obj.heart_rate.split(',')]
        tData.append(heart_rate_interval)
    rawData = [list(x) for x in zip(*tData)]
    data['rawData'] = rawData
    data['xData'] = xData
    # print(data)
    cache.set(redis_key, data, 3600 * 2)
    return data


@register.simple_tag
def get_heart_rate_trend(num=14):
    """
    获取心率趋势
    @param num: 获取最新num条数据
    @return:
    """
    this_date_str = datetime.today().strftime('%Y%m%d')
    redis_key = RedisKeys.heart_rate_trend.format(date=this_date_str)
    redis_key = f'{redis_key}_{num}'
    redis_data = cache.get(redis_key)
    if redis_data:
        return redis_data
    data = {}
    objs = Fitness.objects.order_by('-run_date')[:num]
    objs = list(objs)[::-1]
    rawData = []
    for obj in objs:
        heart_data = [obj.run_date.strftime('%m-%d')]
        heart_data.extend([int(x) for x in obj.five_heart_rate.split(',')])
        heart_data.append(obj.average_heart_rate)
        rawData.append(heart_data)
    data['rawData'] = rawData
    # print(data)
    cache.set(redis_key, data, 3600 * 2)
    return data


@register.simple_tag
def get_pace_trend(num=14):
    """
    获取配速趋势
    @param num: 获取最新num条数据
    @return:
    """
    this_date_str = datetime.today().strftime('%Y%m%d')
    redis_key = RedisKeys.pace_trend.format(date=this_date_str)
    redis_key = f'{redis_key}_{num}'
    redis_data = cache.get(redis_key)
    if redis_data:
        return redis_data
    data = {}
    objs = Fitness.objects.order_by('-run_date')[:num]
    objs = list(objs)[::-1]
    rawData = []
    for obj in objs:
        pace_data = [obj.run_date.strftime('%m-%d')]
        pace_data.extend([time_to_minutes(x) for x in obj.five_pace.split(',')])
        pace_data.append(time_to_minutes(obj.average_pace))
        rawData.append(pace_data)
    data['rawData'] = rawData
    # print(data)
    cache.set(redis_key, data, 3600 * 2)
    return data


@register.simple_tag
def get_cadence_trend(num=14):
    """
    获取步频趋势
    @param num: 获取最新num条数据
    @return:
    """
    this_date_str = datetime.today().strftime('%Y%m%d')
    redis_key = RedisKeys.cadence_trend.format(date=this_date_str)
    redis_key = f'{redis_key}_{num}'
    redis_data = cache.get(redis_key)
    if redis_data:
        return redis_data
    data = {}
    objs = Fitness.objects.order_by('-run_date')[:num]
    objs = list(objs)[::-1]
    rawData = []
    for obj in objs:
        cadence_data = [obj.run_date.strftime('%m-%d')]
        cadence_data.extend([int(x) for x in obj.five_cadence.split(',')])
        cadence_data.append(obj.average_cadence)
        rawData.append(cadence_data)
    data['rawData'] = rawData
    # print(data)
    cache.set(redis_key, data, 3600 * 2)
    return data
