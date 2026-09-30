"""
article_sync（文章同步 GitHub）单元测试。

背景：API 列表接口 /openapi/v1/articles/ 出于性能考虑不返回 body 字段，
同步脚本必须对"确定要上传"的文章按需请求详情接口拿正文；
且单篇文章处理失败时不能中断整批同步。

测试不依赖 Django（article_sync 只用 requests/yaml），
可脱离 settings 直接运行：python apps/easytask/tests.py
"""
import os
import re
import sys
import unittest
from datetime import datetime, timedelta
from unittest import mock

import requests

# 脱离 Django 单独运行时的 import 引导（Django 环境下 apps 已在 sys.path）
if 'django' not in sys.modules:
    _ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for _p in (_ROOT, os.path.join(_ROOT, 'apps')):
        if _p not in sys.path:
            sys.path.insert(0, _p)

from easytask.action import article_sync

BASE_URL = 'https://blog.example.com'


class FakeBlogApi:
    """
    模拟博客 openapi 的 requests.get：
    - 列表接口返回 results（模拟线上行为：不含 body 字段）
    - 详情接口 /articles/{id}/ 返回带 body 的完整数据
    - fail_ids 中的 id 请求详情时抛连接异常
    """

    def __init__(self, list_items, detail_bodies, fail_ids=()):
        self.list_items = list_items
        self.detail_bodies = detail_bodies
        self.fail_ids = set(fail_ids)

    def __call__(self, url, **kwargs):
        if url.endswith('/openapi/v1/articles/'):
            resp = mock.Mock()
            resp.json.return_value = {'results': self.list_items, 'next': None}
            return resp
        m = re.search(r'/openapi/v1/articles/(\d+)/$', url)
        if m:
            pk = int(m.group(1))
            if pk in self.fail_ids:
                raise requests.exceptions.ConnectionError(f'detail {pk} failed')
            resp = mock.Mock()
            resp.json.return_value = {'id': pk, 'body': self.detail_bodies[pk]}
            return resp
        raise AssertionError(f'unexpected request: {url}')


class ArticleSyncTest(unittest.TestCase):

    def _make_manager(self, full=True):
        gh = mock.Mock()
        gh.upload_file.return_value = {'ok': True}
        manager = article_sync.BlogManager(
            base_url=BASE_URL, base64_string='dXNlcjpwYXNz', github_manager=gh,
            source_media_url='https://blog.example.com/cdn/',
            target_media_url='https://cdn.example.com/',
            full=full,
        )
        return manager, gh

    @staticmethod
    def _item(pk, slug, update=None):
        """模拟列表接口返回的文章条目（与线上一致：没有 body 字段）"""
        update = update or datetime.now()
        return {
            'id': pk,
            'slug': slug,
            'title': f'Title {slug}',
            'subject': None,
            'update_date': f'{update:%Y-%m-%dT%H:%M:%S}',
        }

    def test_upload_article_fetches_body_from_detail_api(self):
        """列表条目没有 body 时，应请求详情接口拿正文再上传"""
        manager, gh = self._make_manager(full=True)
        item = self._item(42, 'hello')
        api = FakeBlogApi(list_items=[item], detail_bodies={42: 'raw **body**'})
        with mock.patch.object(article_sync.requests, 'get', side_effect=api):
            manager.upload_article(item)
        gh.upload_file.assert_called_once()
        file_path, body = gh.upload_file.call_args[0]
        self.assertEqual(file_path, 'blog/free/hello.md')
        self.assertIn('raw **body**', body)
        self.assertIn('# Title hello', body)

    def test_upload_all_articles_continues_after_single_failure(self):
        """一篇文章取正文失败只记录错误，不影响后续文章上传"""
        manager, gh = self._make_manager(full=True)
        bad = self._item(1, 'bad')
        ok = self._item(2, 'ok')
        api = FakeBlogApi(list_items=[bad, ok],
                          detail_bodies={2: 'good body'}, fail_ids={1})
        with mock.patch.object(article_sync.requests, 'get', side_effect=api):
            manager.upload_all_articles(manager.article_start_url)
        self.assertEqual(gh.upload_file.call_count, 1)
        self.assertEqual(gh.upload_file.call_args[0][0], 'blog/free/ok.md')
        self.assertEqual(manager.result['blog']['sync_failed'], 1)
        self.assertEqual(manager.result['blog']['errors'][0]['slug'], 'bad')

    def test_skipped_article_never_fetches_body(self):
        """超过 60 天被过滤的文章不应发起任何请求（详情按需拉取的前提）"""
        manager, gh = self._make_manager(full=True)
        old_item = self._item(9, 'old', update=datetime.now() - timedelta(days=61))
        api = FakeBlogApi(list_items=[old_item], detail_bodies={})
        with mock.patch.object(article_sync.requests, 'get', side_effect=api) as mock_get:
            manager.upload_article(old_item)
        mock_get.assert_not_called()
        gh.upload_file.assert_not_called()


if __name__ == '__main__':
    unittest.main()
