from django import template
from django.core.cache import cache

from blog.utils import RedisKeys

register = template.Library()


@register.simple_tag
def get_views_data_from_redis():
    """
    从redis里面获取文章访问量数据，获取不到则返回空格式
    @return:
    """
    redis_key = RedisKeys.views_statistics
    redis_data = cache.get(redis_key)
    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    data = [['product', '本周阅读量', '上周阅读量']]
    if not redis_data:
        for day in days:
            data.append([day, '-', '-'])
    else:
        last_week = redis_data['last_week_views']
        this_week = redis_data['this_week_views']
        for day in days:
            data.append([day, this_week.get(day, '-'), last_week.get(day, '-')])
    return data
