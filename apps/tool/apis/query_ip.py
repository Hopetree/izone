# -*- coding:utf-8 -*-
import requests


class QueryIPApi:

    def __init__(self, ip):
        self.ip = ip

    def baidu_api(self):
        if not self.ip.strip():
            return {'code': 'MissingParameter', 'charge': False, 'msg': 'IP地址为空'}

        url = 'https://qifu-api.baidubce.com/ip/geo/v1/district?ip=%s' % self.ip
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)
        return response.json()


if __name__ == '__main__':
    """
    {'code': 'Success', 'data': {'continent': '亚洲', 'country': '中国', 'zipcode': '518023', 'timezone': 'UTC+8', 'accuracy': '区县', 'owner': '中国电信', 'isp': '中国电信', 'source': '数据挖掘', 'areacode': 'CN', 'adcode': '440305', 'asnumber': '4134', 'lat': '22.556244', 'lng': '113.939291', 'radius': '25.3318', 'prov': '广东省', 'city': '深圳市', 'district': '南山区'}, 'charge': True, 'msg': '查询成功', 'ip': '116.31.232.85', 'coordsys': 'WGS84'}
    """
    from pprint import pprint

    api = QueryIPApi('')
    # api = QueryIPApi('66.90.98.178')
    print(api.baidu_api())
