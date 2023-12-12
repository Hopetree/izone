import json
from datetime import datetime, timedelta
from django import template
from django.core.cache import cache

from blog.utils import RedisKeys
from blog.models import ArticleView, Article

register = template.Library()


@register.simple_tag
def get_views_data_from_redis(t1, t2):
    """
    从redis里面获取文章访问量数据，获取不到则返回空格式
    @return:
    """
    redis_key = RedisKeys.views_statistics
    redis_data = cache.get(redis_key)
    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    data = [['product', t1, t2]]
    if not redis_data:
        for day in days:
            data.append([day, '-', '-'])
    else:
        last_week = redis_data['last_week_views']
        this_week = redis_data['this_week_views']
        for day in days:
            data.append([day, this_week.get(day, '-'), last_week.get(day, '-')])
    return data


def get_hours_data_by_date(date):
    """
    获取一个日期的小时数据
    @param date:
    @return: dict
    """
    obj = ArticleView.objects.filter(date=date)
    if obj and json.loads(obj.first().body).get('every_hours'):
        return json.loads(obj.first().body).get('every_hours')
    return {}


@register.simple_tag
def get_hours_views_from_redis(t1, t2):
    """
    从redis获取当天和昨天每小时的阅读量，获取不到则返回空格式
    @return:
    """
    this_hour = datetime.now().strftime('%Y%m%d%H')
    redis_key = RedisKeys.hours_views_statistics.format(hour=this_hour)
    redis_value = cache.get(redis_key)
    if redis_value:
        return redis_value
    else:
        data = [['product', t1, t2]]
        pre_date_str = (datetime.today() - timedelta(days=2)).strftime('%Y%m%d')  # 前天
        yes_date_str = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')  # 昨天
        thi_date_str = datetime.today().strftime('%Y%m%d')  # 今天
        pre_hours_data = get_hours_data_by_date(pre_date_str)
        yes_hours_data = get_hours_data_by_date(yes_date_str)
        thi_hours_data = get_hours_data_by_date(thi_date_str)
        hour_list = [str(h).zfill(2) for h in range(0, 24)]
        for hour in hour_list:
            if hour == '00':
                if thi_hours_data.get(hour) and yes_hours_data.get('23'):
                    thi_value = thi_hours_data[hour] - yes_hours_data['23']  # 今天00点访问量
                else:
                    thi_value = '-'
                if yes_hours_data.get(hour) and pre_hours_data.get('23'):
                    yes_value = yes_hours_data[hour] - pre_hours_data['23']  # 昨天00点访问量
                else:
                    yes_value = '-'
            else:
                last_hour = str(int(hour) - 1).zfill(2)
                if thi_hours_data.get(hour) and thi_hours_data.get(last_hour):
                    thi_value = thi_hours_data[hour] - thi_hours_data[last_hour]
                else:
                    thi_value = '-'
                if yes_hours_data.get(hour) and yes_hours_data.get(last_hour):
                    yes_value = yes_hours_data[hour] - yes_hours_data[last_hour]
                else:
                    yes_value = '-'
            data.append([hour, thi_value, yes_value])
        cache.set(redis_key, data, 3600)  # 缓存1小时即可，每小时必须更新
        return data


@register.simple_tag
def get_hot_article_list():
    """
    获取昨日热门文章，元数据来自于定时任务统计的每日阅读量数据
    验证：有删除，新增文章的操作，不能报错
    只保留10篇文章就行，且都需要有阅读量的增加
    @return:
    """
    yesterday_str = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')  # 昨天
    last_day_str = (datetime.today() - timedelta(days=2)).strftime('%Y%m%d')  # 前天
    redis_key = RedisKeys.hot_article_list.format(date=yesterday_str)
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
                if article_obj_query and each['value']:
                    article_obj = article_obj_query.first()
                    article_obj.add_view = each['value']
                    result.append(article_obj)
                    if len(result) >= 10:
                        break
            cache.set(redis_key, result, 3600 * 24)  # 缓存一天即可，反正到了新一天自动更换key
            return result
    return []
