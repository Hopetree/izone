from django.db import models
from django.conf import settings
from blog.models import Article
import re

import markdown

emoji_info = [
    [('aini_org', '爱你'), ('baibai_thumb', '拜拜'),
     ('baobao_thumb', '抱抱'), ('beishang_org', '悲伤'),
     ('bingbujiandan_thumb', '并不简单'), ('bishi_org', '鄙视'),
     ('bizui_org', '闭嘴'), ('chanzui_org', '馋嘴')],
    [('chigua_thumb', '吃瓜'), ('chongjing_org', '憧憬'),
     ('dahaqian_org', '哈欠'), ('dalian_org', '打脸'),
     ('ding_org', '顶'), ('doge02_org', 'doge'),
     ('erha_org', '二哈'), ('gui_org', '跪了')],
    [('guzhang_thumb', '鼓掌'), ('haha_thumb', '哈哈'),
     ('heng_thumb', '哼'), ('huaixiao_org', '坏笑'),
     ('huaxin_org', '色'), ('jiyan_org', '挤眼'),
     ('kelian_org', '可怜'), ('kuxiao_org', '允悲')],
    [('ku_org', '酷'), ('leimu_org', '泪'),
     ('miaomiao_thumb', '喵喵'), ('ningwen_org', '疑问'),
     ('nu_thumb', '怒'), ('qian_thumb', '钱'),
     ('sikao_org', '思考'), ('taikaixin_org', '太开心')],
    [('tanshou_org', '摊手'), ('tianping_thumb', '舔屏'),
     ('touxiao_org', '偷笑'), ('tu_org', '吐'),
     ('wabi_thumb', '挖鼻'), ('weiqu_thumb', '委屈'),
     ('wenhao_thumb', '费解'), ('wosuanle_thumb', '酸')],
    [('wu_thumb', '污'), ('xiaoerbuyu_org', '笑而不语'),
     ('xiaoku_thumb', '笑cry'), ('xixi_thumb', '嘻嘻'),
     ('yinxian_org', '阴险'), ('yun_thumb', '晕'),
     ('zhouma_thumb', '怒骂'), ('zhuakuang_org', '抓狂')]
]


def get_emoji_imgs(body):
    """
    替换掉评论中的标题表情，并且把表情替换成图片地址
    :param body:
    :return:
    """
    img_url = '<img class="comment-emoji-img" src="/static/comment/weibo/{}.png" title="{}" alt="{}">'
    for i in emoji_info:
        for ii in i:
            emoji_url = img_url.format(ii[0], ii[1], ii[0])
            body = re.sub(':{}:'.format(ii[0]), emoji_url, body)
    tag_info = {
        '<h\d>': '',
        '</h\d>': '<br>',
        '<script.*</script>': '',
        '<meta.*?>': '',
        '<link.*?>': ''
    }
    for k, v in tag_info.items():
        body = re.sub(k, v, body)
    return body


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_related',
                               verbose_name='评论人', on_delete=models.CASCADE)
    create_date = models.DateTimeField('创建时间', auto_now_add=True)
    content = models.TextField('评论内容')
    parent = models.ForeignKey('self', verbose_name='父评论', related_name='%(class)s_child_comments',
                               blank=True,
                               null=True, on_delete=models.CASCADE)
    rep_to = models.ForeignKey('self', verbose_name='回复', related_name='%(class)s_rep_comments',
                               blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        """这是一个元类，用来继承的"""
        abstract = True

    def __str__(self):
        return self.content[:20]

    def content_to_markdown(self):
        to_md = markdown.markdown(self.content,
                                  safe_mode='escape',
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                  ])
        return get_emoji_imgs(to_md)


class ArticleComment(Comment):
    belong = models.ForeignKey(Article, related_name='article_comments', verbose_name='所属文章',
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = '文章评论'
        verbose_name_plural = verbose_name
        ordering = ['create_date']


class Notification(models.Model):
    create_p = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='提示创建者',
                                 related_name='notification_create',
                                 on_delete=models.CASCADE)
    get_p = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='提示接收者',
                              related_name='notification_get',
                              on_delete=models.CASCADE)
    comment = models.ForeignKey(ArticleComment, verbose_name='所属评论', related_name='the_comment',
                                on_delete=models.CASCADE)
    create_date = models.DateTimeField('提示时间', auto_now_add=True)
    is_read = models.BooleanField('是否已读', default=False)

    def mark_to_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])

    class Meta:
        verbose_name = '提示信息'
        verbose_name_plural = verbose_name
        ordering = ['-create_date']

    def __str__(self):
        return '{}@了{}'.format(self.create_p, self.get_p)

    @property
    def tag(self):
        """评论的提示"""
        return "comment"


class BaseNotification(models.Model):
    """推送基类"""
    get_p = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='收信人',
                                   related_name='%(class)s_recipient', blank=False)
    create_date = models.DateTimeField('推送时间', auto_now_add=True)
    is_read = models.BooleanField('是否已读', default=False)

    class Meta:
        """这是一个元类，用来继承的"""
        abstract = True

    def mark_to_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])


class SystemNotification(BaseNotification):
    title = models.CharField(verbose_name='标题', max_length=50)
    content = models.TextField(verbose_name='通知内容', help_text='支持html格式的内容')

    class Meta:
        verbose_name = '系统通知'
        verbose_name_plural = verbose_name
        ordering = ['-create_date']

    def __str__(self):
        return self.title

    @property
    def tag(self):
        """系统通知"""
        return "system"
