# -*- coding:utf-8 -*-
import json
import time
import re

import requests


class QueryIPApi:

    def __init__(self, ip):
        self.ip = ip
        self.none_ip_result = {'code': 'MissingParameter', 'msg': 'IP地址为空'}
        self.bad_request = {'code': 'BadRequest', 'msg': '获取IP信息失败'}

    def baidu_api(self):
        """
        {'code': 'Success', 'data': {'continent': '亚洲', 'country': '中国', 'zipcode': '518023', 'timezone': 'UTC+8', 'accuracy': '区县', 'owner': '中国电信', 'isp': '中国电信', 'source': '数据挖掘', 'areacode': 'CN', 'adcode': '440305', 'asnumber': '4134', 'lat': '22.556244', 'lng': '113.939291', 'radius': '25.3318', 'prov': '广东省', 'city': '深圳市', 'district': '南山区'}, 'charge': True, 'msg': '查询成功', 'ip': '116.31.232.85', 'coordsys': 'WGS84'}
        """
        url = 'https://qifu-api.baidubce.com/ip/geo/v1/district?ip=%s' % self.ip
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
        try:
            response = requests.get(url, headers=headers)
            result = response.json()
            result['resource_id'] = '0'  # 添加来源信息，前端根据不同来源进行展示
            return result
        except json.decoder.JSONDecodeError:
            self.bad_request['resource_id'] = '0'
            return self.bad_request

    def ip_locate_api(self):
        self.bad_request['resource_id'] = '1'
        """
        {'ip': '14.31.232.85', 'country': 'China', 'country_code': 'CN', 'is_eu': False, 'city': None, 'continent': 'Asia', 'latitude': 34.7732, 'longitude': 113.722, 'time_zone': 'Asia/Shanghai', 'postal_code': None, 'subdivision': None, 'subdivision2': None, 'network': '14.31.0.0/16', 'org': 'Chinanet', 'asn': 'AS4134', 'asn_network': '14.24.0.0/13', 'threat': {'is_proxy': False}, 'code': 'Success', 'resource_id': '1'}
        """
        url = 'https://www.iplocate.io/api/lookup-preview/%s' % self.ip
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Referer': 'https://www.iplocate.io/',
            'Cookie': '_iplocate_io_session=anything{}'.format(time.time())}
        try:
            response = requests.get(url, headers=headers)
            result = response.json()
            if result.get('error'):
                return self.bad_request
            else:
                result['code'] = 'Success'
            result['resource_id'] = '1'
            return result
        except json.decoder.JSONDecodeError:
            return self.bad_request

    def ip_info_api(self):
        self.bad_request['resource_id'] = '2'
        """
        {"input":"66.90.98.172","data":{"ip":"66.90.98.172","city":"Singapore","region":"Singapore","country":"SG","loc":"1.2897,103.8501","org":"AS30058 FDCservers.net","postal":"018989","timezone":"Asia/Singapore","asn":{"asn":"AS30058","name":"FDCservers.net","domain":"fdcservers.net","route":"66.90.98.0/24","type":"isp"},"company":{"name":"FDCservers.net","domain":"fdcservers.net","type":"isp"},"privacy":{"vpn":false,"proxy":false,"tor":false,"relay":false,"hosting":false,"service":""},"abuse":{"address":"US, FL, Destin, 175 Main St. #1363, 32540","country":"US","email":"abuse@fdcservers.net","name":"ABUSE department","network":"66.90.98.0/24","phone":"+1-312-423-6675"}}}
        """
        url = 'https://ipinfo.io/widget/demo/%s' % self.ip
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Referer': 'https://ipinfo.io/'}
        try:
            response = requests.get(url, headers=headers)
            result = response.json()
            result['code'] = 'Success'
            result['resource_id'] = '2'
            return result
        except json.decoder.JSONDecodeError:
            return self.bad_request

    def ip138(self):
        self.bad_request['resource_id'] = '00'
        url = 'https://www.ipshudi.com/%s.htm' % self.ip
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Referer': 'https://baidu.com/'}
        response = requests.get(url, headers=headers)
        html = response.text
        ip_address = re.findall(r'<td class="th">归属地</td>\n<td>\n<span>(.*?)</span>', html)
        isp = re.findall(r'<td class="th">运营商</td><td><span>(.*?)</span>', html)
        if ip_address:
            result = {'address': ip_address[0].strip(),
                      'isp': isp[0].strip() if isp else '',
                      'code': 'Success', 'resource_id': '00',
                      }
            result_ip_locate = self.ip_locate_api()
            if result_ip_locate.get('code') == 'Success' and result_ip_locate.get('longitude'):
                result['loc'] = '{},{}'.format(result_ip_locate.get('longitude'),
                                               result_ip_locate.get('latitude'))
            else:
                result_ip_info = self.ip_info_api()
                if result_ip_info.get('code') == 'Success' and result_ip_info.get('loc'):
                    result['loc'] = result_ip_info.get('loc')
            return result
        return self.bad_request

    def get_ip_info(self):
        if not self.ip.strip():
            return self.none_ip_result

        # 百度请求错误或者IP被封，则使用其他接口
        result = self.baidu_api()
        if result['code'] in ['Throttling', 'BadRequest']:
            result = self.ip138()
        if result['code'] in ['BadRequest']:
            result = self.ip_locate_api()
        if result['code'] in ['BadRequest']:
            result = self.ip_info_api()
        return result


if __name__ == '__main__':
    from pprint import pprint

    api = QueryIPApi('116.1.32.85')
    # api = QueryIPApi('66.90.98.178')
    # pprint(api.baidu_api())
    # pprint(api.ip_locate_api())
    # pprint(api.ip_info_api())
    # pprint(api.ip138())
    pprint(api.get_ip_info())
