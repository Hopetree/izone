import json
from datetime import datetime, timedelta
from django import template
from django.core.cache import cache

from blog.utils import RedisKeys
from blog.models import ArticleView, Article

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


@register.simple_tag
def get_hot_article_list():
    """
    获取昨日热门文章，元数据来自于定时任务统计的每日阅读量数据
    验证：有删除，新增文章的操作，不能报错
    @return:
    """
    yesterday_str = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')  # 昨天
    last_day_str = (datetime.today() - timedelta(days=2)).strftime('%Y%m%d')  # 前天
    redis_key = f'{RedisKeys.hot_article_list}.{yesterday_str}'
    redis_value = cache.get(redis_key)
    if redis_value:
        return redis_value
    else:
        yesterday_obj = ArticleView.objects.filter(date=yesterday_str)
        yesterday_data = yesterday_obj.first().body if yesterday_obj else None
        last_day_obj = ArticleView.objects.filter(date=last_day_str)
        last_day_data = last_day_obj.first().body if last_day_obj else None
        if yesterday_data and last_day_data:
            yesterday_views = json.loads(yesterday_data)['today_views']
            last_day_views = json.loads(last_day_data)['today_views']
            # 取昨天的数据，前天不存在的文章默认就是0
            result = {key: yesterday_views[key] - last_day_views.get(key, 0) for key in
                      yesterday_views}
            sorted_obj = sorted([(key, value) for key, value in result.items()], key=lambda x: x[1],
                                reverse=True)
            data = [{'key': key, 'value': value} for key, value in sorted_obj]
            result = []
            for each in data:
                article_obj_query = Article.objects.filter(id=each['key'])
                if article_obj_query:
                    article_obj = article_obj_query.first()
                    article_obj.add_view = each['value']
                    result.append(article_obj)
            cache.set(redis_key, result, 3600 * 24)  # 缓存一天即可，反正到了新一天自动更换key
            return result
    return []
