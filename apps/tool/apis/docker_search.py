# -*- coding:utf-8 -*-
# Author: https://github.com/Hopetree
# Date: 2019/8/21
import json
import requests

requests.packages.urllib3.disable_warnings()


class DockerSearch(object):
    base_url = 'https://registry.hub.docker.com/v2/repositories/{repo}/tags/'

    def __init__(self, name):
        self.name = name
        self.url = self.get_url()
        self.results = []
        self.max_page = 3
        self.page_num = 1
        self.next_url = None

    def get_url(self):
        if '/' not in self.name:
            repo = 'library/' + self.name
        else:
            repo = self.name
        url = self.base_url.format(repo=repo)
        return url

    def get_items(self, url):
        try:
            req = requests.get(url, verify=False, timeout=5)
        except:
            return
        else:
            res = req.text
            try:
                data = json.loads(res)
            except:
                return
            else:
                results = data.get('results')
                if results:
                    self.results.extend(results)

                next_url = data.get('next')
                self.page_num += 1
                self.next_url = next_url

                if self.page_num <= self.max_page and next_url:
                    self.get_items(next_url)

    def main(self):
        self.get_items(self.url)
        if not self.results:
            return {
                'status': 403,
                'error': '镜像仓库没有查询到与 {} 相关的镜像信息，请检查镜像名称后重试！'.format(self.name)
            }
        return {
            'status': 200,
            'results': self.results,
            'next_url': self.next_url
        }


if __name__ == '__main__':
    ds = DockerSearch('nginx')
    r = ds.main()
    print(r)
