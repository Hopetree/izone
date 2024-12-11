import re
import json
from datetime import datetime

from django.db import models
from django.db.utils import IntegrityError
from django.conf import settings
from django.shortcuts import reverse
from django.core.exceptions import ValidationError

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import markdown


# Create your models here.

# 文章关键词，用来作为SEO中keywords
class Keyword(models.Model):
    name = models.CharField('文章关键词', max_length=20)

    class Meta:
        verbose_name = '关键词'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name


# 文章标签
class Tag(models.Model):
    name = models.CharField('文章标签', max_length=20)
    slug = models.SlugField(unique=True)
    description = models.TextField('描述', max_length=240, default='标签描述',
                                   help_text='用来作为SEO中description,长度参考SEO标准')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})

    def get_article_list(self):
        """返回当前标签下所有发表的文章列表"""
        return Article.objects.filter(tags=self, is_publish=True)


# 文章分类
class Category(models.Model):
    name = models.CharField('文章分类', max_length=20)
    slug = models.SlugField(unique=True)
    description = models.TextField('描述', max_length=240, default='分类描述',
                                   help_text='用来作为SEO中description,长度参考SEO标准')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})

    def get_article_list(self):
        return Article.objects.filter(category=self, is_publish=True)


# 专题
class Subject(models.Model):
    STATUS_CHOICES = (
        ('not_started', '未开始'),
        ('ongoing', '连载中'),
        ('completed', '已完结'),
    )

    name = models.CharField('专题名称', max_length=50)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='not_started')
    description = models.CharField('描述', max_length=250)
    sort_order = models.IntegerField('排序', default=99, help_text='作为专题列表页的排序')
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    cover_image = ProcessedImageField(upload_to='subject/upload/%Y/%m/%d/',
                                      default='subject/default/default.png',
                                      verbose_name='封面图',
                                      processors=[ResizeToFill(250, 150)],
                                      help_text='上传图片大小建议使用5:3的宽高比，为了清晰度原始图片宽度应该超过250px'
                                      )

    class Meta:
        verbose_name = '专题'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:subject_page', kwargs={'pk': self.pk})

    def get_topics(self):
        """得到一个专题的所有主题，按照排序进行排序"""
        return Topic.objects.filter(subject=self).order_by('sort_order', '-pk')

    def get_article_count(self):
        """获取专题下文章数量"""
        num = 0
        for each in self.get_topics():
            num += each.get_articles().count()
        return num

    def get_article_list(self):
        """
        返回一个专题下文章的列表，这个跟显示的一致，可以用来得到上下文
        @return:
        """
        article_list = []
        for topic in self.get_topics():
            article_list.extend(topic.get_articles())
        return article_list

    def get_status_color(self):
        """返回对应状态的颜色"""
        text_dict = {
            'not_started': 'danger',
            'ongoing': 'info',
            'completed': 'success'
        }
        return text_dict[self.status]


# 专题的主题，作为专题的目录，专题-主题-文章
class Topic(models.Model):
    name = models.CharField('主题名称', max_length=50)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    sort_order = models.IntegerField('排序', default=99,
                                     help_text='仅作为主题在专题中的排序，类似目录')

    subject = models.ForeignKey(Subject, verbose_name='所属专题', on_delete=models.PROTECT,
                                related_name='topics')

    class Meta:
        verbose_name = '专题-主题'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def __str__(self):
        return f'[{self.subject.name}]{self.name}'

    def get_absolute_url(self):
        return reverse('blog:subject_page', kwargs={'pk': self.subject.pk}) + f'#{self.name}'

    def get_articles(self):
        """得到一个主题的所有已发布的文章，按照主题排序排序"""
        return Article.objects.filter(is_publish=True, topic=self).order_by('topic_order', '-pk')


# 文章
class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者',
                               on_delete=models.PROTECT)
    title = models.CharField(max_length=150, verbose_name='文章标题')
    summary = models.TextField('文章摘要', max_length=230,
                               default='文章摘要等同于网页description内容，请务必填写...')
    body = models.TextField(verbose_name='文章内容')
    img_link = ProcessedImageField(upload_to='article/upload/%Y/%m/%d/',
                                   default='article/default/default.png',
                                   verbose_name='封面图',
                                   processors=[ResizeToFill(250, 150)],
                                   blank=True,
                                   help_text='上传图片大小建议使用5:3的宽高比，为了清晰度原始图片宽度应该超过250px'
                                   )
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    views = models.IntegerField('阅览量', default=0)
    slug = models.SlugField(unique=True)
    is_top = models.BooleanField('置顶', default=False)
    is_publish = models.BooleanField('是否发布', default=True)

    category = models.ForeignKey(Category, verbose_name='文章分类', on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, verbose_name='标签')
    keywords = models.ManyToManyField(Keyword, verbose_name='文章关键词',
                                      help_text='文章关键词，用来作为SEO中keywords，最好使用长尾词，3-4个足够')

    # 跟专题-主题相关的字段和关系，都是非必填，仅给专题的时候使用，其他地方一概不用
    # 设计上一个专题有多个主题（目录的概念），一个主题可以有多个文章，一个文章只能归属一个主题
    topic = models.ForeignKey(Topic, verbose_name='所属主题', on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='articles')
    topic_order = models.IntegerField('主题中排序', default=99, null=True, blank=True,
                                      help_text='仅作为文章在主题中的排序')
    topic_short_title = models.CharField('主题短标题', max_length=50, null=True, blank=True,
                                         help_text='专门给Topic使用的短标题')

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-create_date']

    def __str__(self):
        return f'{self.title[:30]}...' if len(self.title) > 30 else self.title

    def save(self, *args, **kwargs):
        # 当为更新且is_publish由False变更成True的时候才执行: 发布的文章时间的创建时间以发布时间为准
        if self.pk and self.is_publish and Article.objects.filter(pk=self.pk,
                                                                  is_publish=False).exists():
            self.create_date = datetime.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """优先使用专题地址"""
        if self.topic:
            return self.get_subject_absolute_url()
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def get_subject_absolute_url(self):
        """获取专栏地址"""
        return reverse('blog:subject_detail', kwargs={'slug': self.slug})

    def body_to_markdown(self):
        return markdown.markdown(self.body, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])

    def update_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_pre(self):
        """
        有主题则只能返回这个主题所属专题下的文章，否则返回空，没有主题则按照pk返回同样没有主题的
        @return:
        """
        if self.topic:
            subject_articles = self.topic.subject.get_article_list()
            for index, article in enumerate(subject_articles):
                if article.pk == self.pk and index != 0:
                    return subject_articles[index - 1]
            return

        return Article.objects.filter(id__lt=self.id,
                                      is_publish=True,
                                      topic__isnull=True
                                      ).order_by('-id').first()

    def get_next(self):
        if self.topic:
            subject_articles = self.topic.subject.get_article_list()
            for index, article in enumerate(subject_articles):
                if article.pk == self.pk and index != len(subject_articles) - 1:
                    return subject_articles[index + 1]
            return

        return Article.objects.filter(id__gt=self.id,
                                      is_publish=True,
                                      topic__isnull=True
                                      ).order_by('id').first()

    def get_topic_title(self):
        """仅当有主题的时候优先使用短标题，这个函数给专题使用"""
        if self.topic:
            return self.topic_short_title or self.title
        return self.title


# 时间线
class Timeline(models.Model):
    COLOR_CHOICE = (
        ('primary', '基本-蓝色'),
        ('success', '成功-绿色'),
        ('info', '信息-天蓝色'),
        ('warning', '警告-橙色'),
        ('danger', '危险-红色')
    )
    SIDE_CHOICE = (
        ('L', '左边'),
        ('R', '右边'),
    )
    STAR_NUM = (
        (1, '1颗星'),
        (2, '2颗星'),
        (3, '3颗星'),
        (4, '4颗星'),
        (5, '5颗星'),
    )
    side = models.CharField('位置', max_length=1, choices=SIDE_CHOICE, default='L')
    star_num = models.IntegerField('星星个数', choices=STAR_NUM, default=3)
    icon = models.CharField('图标', max_length=50, default='fa fa-pencil')
    icon_color = models.CharField('图标颜色', max_length=20, choices=COLOR_CHOICE, default='info')
    title = models.CharField('标题', max_length=100)
    update_date = models.DateTimeField('更新时间')
    content = models.TextField('主要内容')

    class Meta:
        verbose_name = '时间线'
        verbose_name_plural = verbose_name
        ordering = ['-update_date']

    def __str__(self):
        return self.title[:20]

    def content_to_markdown(self):
        """支持markdown，但是没必要用，content直接用html写更好"""
        return markdown.markdown(self.content,
                                 extensions=['markdown.extensions.extra', ]
                                 )


# 幻灯片
class Carousel(models.Model):
    number = models.IntegerField('编号', help_text='编号决定图片播放的顺序，图片不要多于5张')
    title = models.CharField('标题', max_length=20, blank=True, null=True, help_text='标题可以为空')
    content = models.CharField('描述', blank=True, null=True, max_length=80)
    img_url = models.CharField('图片地址', max_length=200)
    url = models.CharField('跳转链接', max_length=200, default='#',
                           help_text='图片跳转的超链接，默认#表示不跳转')

    class Meta:
        verbose_name = '图片轮播'
        verbose_name_plural = verbose_name
        # 编号越小越靠前，添加的时间约晚约靠前
        ordering = ['number', '-id']

    def __str__(self):
        return self.title or ''


# 死链
class Silian(models.Model):
    badurl = models.CharField('死链地址', max_length=200,
                              help_text='注意：地址是以http开头的完整链接格式')
    remark = models.CharField('死链说明', max_length=50, blank=True, null=True)
    add_date = models.DateTimeField('提交日期', auto_now_add=True)

    class Meta:
        verbose_name = '死链'
        verbose_name_plural = verbose_name
        ordering = ['-add_date']

    def __str__(self):
        return self.badurl


class FriendLink(models.Model):
    name = models.CharField('网站名称', max_length=50)
    description = models.CharField('网站描述', max_length=100, blank=True)
    link = models.URLField('友链地址', help_text='请填写http或https开头的完整形式地址')
    logo = ProcessedImageField(upload_to='friend/upload/%Y',
                               default='friend/default/default.png',
                               verbose_name='网站LOGO',
                               processors=[ResizeToFill(120, 120)],
                               blank=True,
                               help_text='上传图片大小建议120x120以上，使用友联域名命名，如tendcode.com.png'
                               )
    create_date = models.DateTimeField('创建时间', auto_now_add=True)
    is_active = models.BooleanField('是否有效', default=True)
    is_show = models.BooleanField('是否展示', default=False)
    not_show_reason = models.CharField('禁用原因', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name
        ordering = ['create_date']

    def __str__(self):
        return self.name

    def get_home_url(self):
        """提取友链的主页"""
        u = re.findall(r'(http|https://.*?)/.*?', self.link)
        home_url = u[0] if u else self.link
        return home_url

    def active_to_false(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def show_to_false(self):
        self.is_show = True
        self.save(update_fields=['is_show'])


class AboutBlog(models.Model):
    body = models.TextField(verbose_name='About 内容')
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        verbose_name = 'About'
        verbose_name_plural = verbose_name

    def __str__(self):
        return 'About'

    def body_to_markdown(self):
        return markdown.markdown(self.body, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])


class ArticleView(models.Model):
    date = models.CharField('统计日期', max_length=10, unique=True)  # 唯一性
    body = models.TextField(verbose_name='统计数据')
    create_date = models.DateTimeField(verbose_name='录入时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '文章浏览量统计'
        verbose_name_plural = verbose_name
        ordering = ['create_date']

    def __str__(self):
        return self.date


# 单页面浏览量记录模型，记录一些单页面的浏览量
class PageView(models.Model):
    url = models.CharField('页面地址', max_length=255, unique=True)  # 唯一性
    name = models.CharField('页面名称', max_length=255, blank=True, null=True)
    views = models.IntegerField('浏览量', default=0)
    is_compute = models.BooleanField('是否计算到访问量', default=True)  # 有的页面只记录，不计算
    create_date = models.DateTimeField(verbose_name='录入时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = "单页面浏览量"
        verbose_name_plural = verbose_name
        ordering = ['url']

    def update_views(self):
        self.views += 1
        self.save(update_fields=['views', 'update_date'])


class FeedHub(models.Model):
    name = models.CharField('名称', max_length=50, unique=True)
    url = models.CharField('feed地址', max_length=255)
    icon = models.TextField('图标地址', help_text='可以填写base64图片格式或者图标地址')
    is_active = models.BooleanField('是否有效', help_text='作为是否采集的标识', default=True)
    create_date = models.DateTimeField(verbose_name='录入时间', auto_now_add=True)
    data = models.TextField('数据', help_text='定义任务采集数据', blank=True, null=True)
    sort_order = models.IntegerField('排序', default=99, help_text='作为显示的时候的顺序')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Feed Hub"
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def update_data(self, data):
        self.data = data
        self.save(update_fields=['data'])


class MenuLink(models.Model):
    name = models.CharField('名称', max_length=20, unique=True, help_text='如：Github 主页')
    icon = models.CharField('图标', max_length=20, unique=True, help_text='如：fa-github')
    link = models.CharField('链接', max_length=200, unique=True)
    title = models.CharField('标题', max_length=50, unique=True, help_text='外链的描述')
    active = models.BooleanField('是否有效', help_text='是展示有效的链接', default=True)
    sort_order = models.IntegerField('排序', default=99, help_text='作为显示的时候的顺序')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "菜单外链"
        verbose_name_plural = verbose_name
        ordering = ['sort_order']


class SiteConfig(models.Model):
    config_data = models.TextField(
        "配置数据",
        help_text="配置项作为全局上下文使用，上下文的具体定义见 apps/blog/context_processors.py 文件"
    )

    class Meta:
        verbose_name = "网站配置"
        verbose_name_plural = verbose_name

    def clean(self):
        # 检查config_data是否是合法的JSON格式
        try:
            json_data = json.loads(self.config_data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"无效的JSON格式: {e}")

        # 校验必填键
        required_keys = ["site_logo_name", "site_base_title",
                         "site_end_title", "site_description", "site_keywords",
                         "site_create_date"]
        for key in required_keys:
            if key not in json_data:
                raise ValidationError(f"缺少配置项: {key}")

        # 校验格式，除了指定的字段，其他都必须是字符串
        key_type_dict = {
            'site_show_register': bool
        }
        for key, value in json_data.items():
            if key in key_type_dict:
                if not isinstance(value, key_type_dict[key]):
                    raise ValidationError(f"配置项{key}必须是{key_type_dict[key]}类型")
            else:
                if not isinstance(value, str):
                    raise ValidationError(f"配置项{key}必须是字符串")

        # 校验 site_create_date 是否符合 %Y-%m-%d 格式
        try:
            site_create_date = json_data.get('site_create_date')
            datetime.strptime(site_create_date, '%Y-%m-%d')
        except (ValueError, TypeError):
            raise ValidationError("site_create_date 必须是 %Y-%m-%d 格式的日期")

        # 校验 site_http_type 只能是 http 或 https
        if json_data.get('site_http_type'):
            if json_data.get('site_http_type').lower() not in ['http', 'https']:
                raise ValidationError("site_http_type 必须是 http 或 https")

    def save(self, *args, **kwargs):
        # 确保只存在一个配置实例
        if SiteConfig.objects.exists() and not self.pk:
            raise IntegrityError("只能存在一个网站配置实例")
        super().save(*args, **kwargs)


class Fitness(models.Model):
    location = models.CharField('位置', max_length=50, default='深圳')
    run_date = models.DateTimeField('跑步时间', help_text='跑步开始时间')
    # 详细信息
    training_duration = models.CharField('训练时长', max_length=7, help_text='如：0:35:12')
    distance = models.FloatField('距离(公里)', help_text='如：5.03')
    active_kcal = models.IntegerField('动态千卡', help_text='如：301')
    total_kcal = models.IntegerField('总千卡数', help_text='如：352')
    total_elevation_gain = models.IntegerField('总爬升高度(米)', default=2, help_text='如：2')
    average_power = models.IntegerField('平均功率(瓦)', help_text='如：117')
    average_cadence = models.IntegerField('平均步频(步/分)', help_text='如：180')
    average_pace = models.CharField('平均配速', max_length=7, help_text='如：8:23')
    average_heart_rate = models.IntegerField('平均心率(次/分)', help_text='如：142')
    average_stride_length = models.FloatField('平均步长(米)', default=0.7, help_text='如：0.7')
    bottom_time = models.IntegerField('触底时间(毫秒)', help_text='如：267')
    vertical_amplitude = models.FloatField('垂直振幅(厘米)', default=7.9, help_text='如：7.9')
    # 5段数据，用逗号分割
    five_pace = models.CharField('5段配速', max_length=50, help_text='如：8:23,8:23,8:23,8:23,8:23')
    five_heart_rate = models.CharField('5段心率', max_length=50, help_text='如：142,145,150,156,160')
    five_power = models.CharField('5段功率', max_length=50, help_text='如：117,117,114,113,112')
    five_cadence = models.CharField('5段步频', max_length=50, help_text='如：180,180,178,178,178')
    # 心率区间分布，用逗号分割
    heart_rate = models.CharField('心率区间分布', max_length=50,
                                  help_text='如：04:47,34:22,02:54,00:00,00:00')

    def __str__(self):
        return self.run_date.strftime('%Y-%m-%d %H:%M')

    class Meta:
        verbose_name = "健身"
        verbose_name_plural = verbose_name
        ordering = ['run_date']

    def clean(self):
        if len(self.training_duration.split(':')) != 3:
            raise ValidationError("训练时长格式应该是 0:35:12 这种")
        if len(self.average_pace.split(':')) != 2:
            raise ValidationError("平均配速格式应该是 5:12 这种")
        for value in [self.five_pace, self.five_heart_rate, self.five_power, self.five_cadence,
                      self.heart_rate]:
            if len(value.split(',')) != 5:
                raise ValidationError(f"{value} 不满足5段数据格式")
        for each in self.five_pace.split(','):
            if each and len(each.split(':')) != 2:
                raise ValidationError(f"{each} 不满足5段配速时间格式")
        for each in self.heart_rate.split(','):
            if each and len(each.split(':')) != 2:
                raise ValidationError(f"{each} 不满足心率区间的时间格式")

    def get_absolute_url(self):
        return reverse('blog:health')
