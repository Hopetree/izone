from django.db import models
from django.conf import settings
from blog.models import Article

import markdown
import emoji


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_related', verbose_name='评论人')
    create_date = models.DateTimeField('创建时间', auto_now_add=True)
    content = models.TextField('评论内容')
    parent = models.ForeignKey('self', verbose_name='父评论', related_name='%(class)s_child_comments', blank=True,
                               null=True)
    rep_to = models.ForeignKey('self', verbose_name='回复', related_name='%(class)s_rep_comments', blank=True, null=True)

    class Meta:
        '''这是一个元类，用来继承的'''
        abstract = True

    def __str__(self):
        return self.content[:20]

    def content_to_markdown(self):
        # 先转换成emoji然后转换成markdown,'escape':所有原始HTML将被转义并包含在文档中
        to_emoji_content = emoji.emojize(self.content, use_aliases=True)
        to_md = markdown.markdown(to_emoji_content,
                                  safe_mode='escape',
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                  ])
        return to_md

class ArticleComment(Comment):
    belong = models.ForeignKey(Article, related_name='article_comments', verbose_name='所属文章')

    class Meta:
        verbose_name = '文章评论'
        verbose_name_plural = verbose_name
        ordering = ['create_date']

class Notification(models.Model):
    create_p = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='提示创建者',related_name='notification_create')
    get_p = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='提示接收者',related_name='notification_get')
    comment = models.ForeignKey(ArticleComment,verbose_name='所属评论',related_name='the_comment')
    create_date = models.DateTimeField('提示时间',auto_now_add=True)
    is_read = models.BooleanField('是否已读',default=False)

    def mark_to_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])

    class Meta:
        verbose_name = '提示信息'
        verbose_name_plural = verbose_name
        ordering = ['-create_date']

    def __str__(self):
        return '{}@了{}'.format(self.create_p,self.get_p)