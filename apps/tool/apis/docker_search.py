# -*- coding:utf-8 -*-
# Author: https://github.com/Hopetree
# Date: 2019/8/21
import json
import requests

requests.packages.urllib3.disable_warnings()


class DockerSearch(object):
    # base_url = 'https://registry.hub.docker.com/v2/repositories/{repo}/tags/'
    base_url = 'https://cf-workers-docker-io-e7p.pages.dev/v2/repositories/{repo}/tags/'
    STATUS_404 = 404
    STATUS_500 = 500

    def __init__(self, name):
        self.name = name
        self.max_page = 2
        self.page_num = 1
        self.code = 200
        self.page_size = 25
        self.parmas = '?page_size={}&page={}&ordering=last_updated'
        self.url = self.get_url()
        self.results = []

    def get_url(self):
        if '/' not in self.name:
            repo = 'library/' + self.name
        else:
            repo = self.name
        url = self.base_url.format(repo=repo) + self.parmas.format(self.page_size, self.page_num)
        return url

    def get_items(self, url):
        try:
            req = requests.get(url, verify=False, timeout=5)
        except requests.exceptions.RequestException:
            self.code = self.STATUS_500
            return
        else:
            res = req.text
            if req.status_code != 200:
                self.code = self.STATUS_404
                return
            data = json.loads(res)
            results = data.get('results')
            if results:
                self.results.extend(results)

            self.page_num += 1

            if len(results) >= self.page_size and self.page_num <= self.max_page:
                self.get_items(self.get_url())

    def main(self):
        '''
        总共三种状态，有查询结果返回200，无结果 >（超时返回500，其他都返回404）
        :return:
        '''
        self.get_items(self.url)
        if not self.results:
            if self.code == self.STATUS_500:
                return {
                    'status': self.code,
                    'error': '哎呀！！！网络拥堵...查询官方接口超时，请稍后重试'
                }
            else:
                return {
                    'status': self.code,
                    'error': '镜像仓库没有查询到与 {} 相关的镜像信息，请检查镜像名称后重试！'.format(
                        self.name)
                }
        return {
            'status': 200,
            'results': self.results,
            'next_url': self.next_url,
            'total': len(self.results)
        }


if __name__ == '__main__':
    ds = DockerSearch('nginx')
    r = ds.main()
    print(r)
