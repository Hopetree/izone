from django.test import TestCase
import datetime

# Create your tests here.

from django.urls import reverse


class ArticleAdminUrlTestCase(TestCase):

    def test_edit_blog_url(self):
        change_url = reverse('admin:blog_article_change', args=[61])
        self.assertEqual('/adminx/blog/article/61/change/', change_url)
