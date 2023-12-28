import json
import logging
from datetime import datetime, timedelta
from django import template
from django.core.cache import cache
from django.shortcuts import reverse
from django.urls.exceptions import NoReverseMatch

from blog.utils import RedisKeys
from blog.models import ArticleView, Article, PageView
from easytask.actions import ArticleViewsTool
from oauth.models import Ouser

logger = logging.getLogger(__name__)
register = template.Library()


def get_today_views_by_forecast():
    """
    预测今天的访问量总数，根据昨天每小时和今天已经生成的小时数据进行预测，数据越多应该越接近
    @return:
    """
    result = ('-', '-')
    last_week_date_str = (datetime.today() - timedelta(days=7)).strftime('%Y%m%d')  # 上周今天
    last_week_yes_str = (datetime.today() - timedelta(days=8)).strftime('%Y%m%d')  # 上周昨天
    yes_date_str = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')  # 昨天
    thi_date_str = datetime.today().strftime('%Y%m%d')  # 今天
    last_hour = (datetime.now() - timedelta(hours=1)).strftime('%H')  # 拿到前一个小时的数据，当前还没有
    last_week_article_hours = ArticleViewsTool.get_date_value_by_key(last_week_date_str,
                                                                     'article_every_hours')
    last_week_page_hours = ArticleViewsTool.get_date_value_by_key(last_week_date_str,
                                                                  'page_every_hours')
    last_week_yes_article_hours = ArticleViewsTool.get_date_value_by_key(last_week_yes_str,
                                                                         'article_every_hours')
    last_week_yes_page_hours = ArticleViewsTool.get_date_value_by_key(last_week_yes_str,
                                                                      'page_every_hours')
    yes_article_hours = ArticleViewsTool.get_date_value_by_key(yes_date_str,
                                                               'article_every_hours')
    yes_page_hours = ArticleViewsTool.get_date_value_by_key(yes_date_str, 'page_every_hours')
    thi_article_hours = ArticleViewsTool.get_date_value_by_key(thi_date_str,
                                                               'article_every_hours')
    thi_page_hours = ArticleViewsTool.get_date_value_by_key(thi_date_str, 'page_every_hours')
    # 如果有上周的今天的数据，则使用上周数据，否使用昨天数据
    if all([last_week_article_hours.get('23'), last_week_page_hours.get('23'),
            last_week_article_hours.get(last_hour), last_week_page_hours.get(last_hour),
            yes_article_hours.get('23'), yes_page_hours.get('23'),
            thi_article_hours.get(last_hour), thi_page_hours.get(last_hour),
            last_week_yes_article_hours.get('23'), last_week_yes_page_hours.get('23')]):
        last_week_total_views = last_week_article_hours['23'] + last_week_page_hours['23']
        last_week_done_views = last_week_article_hours[last_hour] + last_week_page_hours[last_hour]
        last_week_yes_total_views = last_week_yes_article_hours['23'] + \
                                    last_week_yes_page_hours['23']
        yes_total_views = yes_article_hours['23'] + yes_page_hours['23']  # 昨日总计
        thi_done_views = thi_article_hours[last_hour] + thi_page_hours[last_hour]  # 今日此时总计
        # 上周今日总*今日当前/上周今日当前
        forecast_views = (last_week_total_views - last_week_yes_total_views) * \
                         (thi_done_views - yes_total_views) / \
                         (last_week_done_views - last_week_yes_total_views)
        last_this_hour_views = last_week_done_views - last_week_yes_total_views
        result = int(forecast_views), last_this_hour_views
    return result


@register.simple_tag
def get_views_data_from_redis():
    """
    从redis里面获取文章访问量数据，获取不到则返回空格式
    @return:
    """
    thi_date_str = datetime.today().strftime('%Y%m%d')
    this_hour = datetime.now().strftime('%Y%m%d%H')
    redis_key = RedisKeys.week_views_statistics.format(hour=this_hour)
    redis_data = cache.get(redis_key)
    if redis_data:
        return redis_data
    else:
        week_data = ArticleViewsTool().get_two_week_data()
        days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        data = []
        last_week = week_data['last_week_views']
        this_week = week_data['this_week_views']
        for day in days:
            if ArticleViewsTool.get_day_of_week(thi_date_str) == day:  # 如果是今天的数据，则预测今天
                forecast_views, done_views = get_today_views_by_forecast()
            else:
                forecast_views, done_views = ('-', '-')
            data.append(
                [day, this_week.get(day, '-'), last_week.get(day, '-'), forecast_views, done_views])
        cache.set(redis_key, data, 3600)
        return data


@register.simple_tag
def get_hours_views_from_redis():
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
        data = []
        pre_date_str = (datetime.today() - timedelta(days=2)).strftime('%Y%m%d')  # 前天
        yes_date_str = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')  # 昨天
        thi_date_str = datetime.today().strftime('%Y%m%d')  # 今天
        pre_article_hours_data = ArticleViewsTool.get_date_value_by_key(pre_date_str,
                                                                        'article_every_hours')
        pre_page_hours_data = ArticleViewsTool.get_date_value_by_key(pre_date_str,
                                                                     'page_every_hours')
        yes_article_hours_data = ArticleViewsTool.get_date_value_by_key(yes_date_str,
                                                                        'article_every_hours')
        yes_page_hours_data = ArticleViewsTool.get_date_value_by_key(yes_date_str,
                                                                     'page_every_hours')
        thi_article_hours_data = ArticleViewsTool.get_date_value_by_key(thi_date_str,
                                                                        'article_every_hours')
        thi_page_hours_data = ArticleViewsTool.get_date_value_by_key(thi_date_str,
                                                                     'page_every_hours')
        hour_list = [str(h).zfill(2) for h in range(0, 24)]
        for hour in hour_list:
            if hour == '00':
                if thi_article_hours_data.get(hour) and yes_article_hours_data.get('23'):
                    thi_article_value = thi_article_hours_data[hour] - yes_article_hours_data['23']
                else:
                    thi_article_value = '-'
                if thi_page_hours_data.get(hour) and yes_page_hours_data.get('23'):
                    thi_page_value = thi_page_hours_data[hour] - yes_page_hours_data['23']
                else:
                    thi_page_value = '-'
                if yes_article_hours_data.get(hour) and pre_article_hours_data.get('23'):
                    yes_article_value = yes_article_hours_data[hour] - pre_article_hours_data['23']
                else:
                    yes_article_value = '-'
                if yes_page_hours_data.get(hour) and pre_page_hours_data.get('23'):
                    yes_page_value = yes_page_hours_data[hour] - pre_page_hours_data['23']
                else:
                    yes_page_value = '-'
            else:
                last_hour = str(int(hour) - 1).zfill(2)
                if thi_article_hours_data.get(hour) and thi_article_hours_data.get(last_hour):
                    thi_article_value = thi_article_hours_data[hour] - thi_article_hours_data[
                        last_hour]
                else:
                    thi_article_value = '-'
                if thi_page_hours_data.get(hour) and thi_page_hours_data.get(last_hour):
                    thi_page_value = thi_page_hours_data[hour] - thi_page_hours_data[last_hour]
                else:
                    thi_page_value = '-'
                if yes_article_hours_data.get(hour) and yes_article_hours_data.get(last_hour):
                    yes_article_value = yes_article_hours_data[hour] - yes_article_hours_data[
                        last_hour]
                else:
                    yes_article_value = '-'
                if yes_page_hours_data.get(hour) and yes_page_hours_data.get(last_hour):
                    yes_page_value = yes_page_hours_data[hour] - yes_page_hours_data[last_hour]
                else:
                    yes_page_value = '-'
            data.append(
                [hour, thi_article_value, thi_page_value, yes_article_value, yes_page_value])
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
        yesterday_views = ArticleViewsTool.get_date_value_by_key(yesterday_str, 'article_views')
        last_day_views = ArticleViewsTool.get_date_value_by_key(last_day_str, 'article_views')
        if yesterday_views and last_day_views:
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
            if result:
                cache.set(redis_key, result, 3600 * 24)  # 缓存一天即可，反正到了新一天自动更换key
                return result
    return []


@register.simple_tag
def get_30_days_views_from_redis():
    this_hour = datetime.now().strftime('%Y%m%d%H')
    redis_key = RedisKeys.month_views_statistics.format(hour=this_hour)
    redis_value = cache.get(redis_key)
    if redis_value:
        return redis_value
    else:
        day_list = [(datetime.today() - timedelta(days=d)).strftime('%Y%m%d') for d in range(31)]
        day_list = list(reversed(day_list))
        data = []
        for day in day_list:
            last_day = (datetime.strptime(day, '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')
            show_day = f'{day[4:6]}-{day[6:8]}'
            last_views_num = ArticleViewsTool.get_date_value_by_key(last_day, 'total_views_num')
            this_views_num = ArticleViewsTool.get_date_value_by_key(day, 'total_views_num')
            if last_views_num and this_views_num:
                add_views = this_views_num - last_views_num
                data.append([show_day, add_views])
            else:
                data.append([show_day, '-'])
        if data:
            cache.set(redis_key, data, 3600)  # 缓存一小时
            return data
    return []


@register.simple_tag
def get_hot_tool_list():
    """
    获取昨日的工具使用热榜，最多返回6篇
    """
    yesterday_str = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')  # 昨天
    last_day_str = (datetime.today() - timedelta(days=2)).strftime('%Y%m%d')  # 前天
    redis_key = RedisKeys.hot_tool_list.format(date=yesterday_str)
    redis_value = cache.get(redis_key)
    if redis_value:
        return redis_value
    else:
        yesterday_views = ArticleViewsTool.get_date_value_by_key(yesterday_str, 'page_views')
        last_day_views = ArticleViewsTool.get_date_value_by_key(last_day_str, 'page_views')
        if yesterday_views and last_day_views:
            # 取昨天的数据，前天不存在的文章默认就是0
            result = {key: yesterday_views[key] - last_day_views.get(key, 0) for key in
                      yesterday_views if key.startswith('tool:')}
            sorted_obj = sorted([(key, value) for key, value in result.items()], key=lambda x: x[1],
                                reverse=True)
            data = [{'key': key, 'value': value} for key, value in sorted_obj]
            result = []
            for each in data:
                try:
                    url_path = reverse(each['key'])  # 解析一下URL，能解析才是有效对象
                    obj_query = PageView.objects.filter(url=each['key'])
                    if obj_query and each['value']:
                        page_obj = obj_query.first()
                        page_obj.add_view = each['value']
                        page_obj.url_path = url_path
                        result.append(page_obj)
                        if len(result) >= 6:
                            break
                except NoReverseMatch:
                    continue
            if result:
                cache.set(redis_key, result, 3600 * 24)  # 缓存一天即可，反正到了新一天自动更换key
                return result
    return []


@register.simple_tag
def get_user_growth_trend():
    this_hour = datetime.now().strftime('%Y%m%d%H')
    redis_key = RedisKeys.user_views_statistics.format(hour=this_hour)
    redis_value = cache.get(redis_key)
    if redis_value:
        return redis_value
    else:
        data = []
        data_dict = {}
        users = Ouser.objects.values_list('date_joined').order_by('date_joined')
        num = 1
        for user in users:
            key = user[0].strftime('%Y-%m-%d')
            if key not in data_dict:
                data_dict[key] = num
            else:
                data_dict[key] += 1
            num += 1
        for k, v in data_dict.items():
            data.append([k, v])
        cache.set(redis_key, data, 3600)
        return data
