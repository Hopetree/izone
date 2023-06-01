# -*- coding:utf-8 -*-
import requests


class QueryIPApi:

    def __init__(self, ip):
        self.ip = ip

    def baidu_api(self):
        url = 'https://qifu-api.baidubce.com/ip/geo/v1/district?ip=%s' % self.ip
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)
        return response.json()


if __name__ == '__main__':
    api = QueryIPApi('116.31.232.85')
    # api = QueryIPApi('66.90.98.178')
    print(api.baidu_api())
