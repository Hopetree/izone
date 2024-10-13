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


def heart_to_list(heart_str):
    """
    心率区间分别输出成百分比，先计算后四个区间，最后一个区间（第一个心率区间）通过减法保证总和为100%
    @param heart_str: 逗号分隔的心率区间字符串，格式类似 "12:30, 15:45, 8:20, 10:15, 7:30"
    @return: 每个心率区间的百分比列表
    """
    # 将心率时间转换为秒
    heart_rates = [time_to_seconds(x) for x in heart_str.split(',')]

    # 计算总时间
    total_time = sum(heart_rates)

    # 计算后四个心率区间的百分比，不进行舍入
    percentages = [(rate / total_time) * 100 for rate in heart_rates[1:]]

    # 对后四个百分比进行舍入并保留一位小数
    rounded_percentages = [round(p, 1) for p in percentages]

    # 第一个心率区间的百分比是 100 - 后四个百分比的和
    first_percentage = round(100 - sum(rounded_percentages), 1)

    # 返回第一个百分比 + 后四个舍入后的百分比
    return [first_percentage] + rounded_percentages


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
def get_heart_rate_interval_v2(num=14):
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
    rawData = []
    for obj in objs:
        heart_rate_interval = [obj.run_date.strftime('%m-%d')]
        heart_rate_interval.extend(heart_to_list(obj.heart_rate))
        rawData.append(heart_rate_interval)
    data['rawData'] = rawData
    # print(data)
    # cache.set(redis_key, data, 3600 * 2)
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
