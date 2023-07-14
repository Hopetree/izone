"""
Django settings for izone project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import sys

# 导入网站个人信息，非通用信息

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加 apps 目录
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('IZONE_SECRET_KEY', '#!kta!9e0)24d@9#=*=ra$r!0k0+p5@w+a%7g1bbof9+ad@4_(')

# 是否开启[在线工具]应用
TOOL_FLAG = os.getenv('IZONE_TOOL_FLAG', 'True').upper() == 'TRUE'
# 是否开启[API]应用
API_FLAG = os.getenv('IZONE_API_FLAG', 'False').upper() == 'TRUE'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('IZONE_DEBUG', 'True').upper() == 'TRUE'

ALLOWED_HOSTS = ['*']

# Application definition

# 添加了新的app需要重启服务器
INSTALLED_APPS = [
    'bootstrap_admin',  # 注册bootstrap后台管理界面,这个必须放在最前面

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # 添加人性化过滤器
    'django.contrib.sitemaps',  # 网站地图

    'oauth',  # 自定义用户应用
    # allauth需要注册的应用
    'django.contrib.sites',  # 这个是自带的，会创建一个sites表，用来存放域名
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.weibo',
    'allauth.socialaccount.providers.github',

    'rest_framework',

    'crispy_forms',  # bootstrap表单样式
    'imagekit',  # 上传图片的应用

    'haystack',  # 全文搜索应用 这个要放在其他应用之前
    'blog',  # 博客应用
    'tool',  # 工具
    'comment',  # 评论
    'django_tctip',
    'resume',  # 个人简历

    'easytask',  # 专门存放celery任务
    'django_celery_results',  # celery结果
    'django_celery_beat',  # celery定时任务

]

# 自定义用户model
AUTH_USER_MODEL = 'oauth.Ouser'

# allauth配置
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# allauth需要的配置
# 当出现"SocialApp matching query does not exist"这种报错的时候就需要更换这个ID
SITE_ID = 2

# 设置登录和注册成功后重定向的页面，默认是/accounts/profile/
LOGIN_REDIRECT_URL = "/"

# Email setting
# 注册中邮件验证方法:“强制（mandatory）”,“可选（optional）【默认】”或“否（none）”之一。
# 开启邮箱验证的话，如果邮箱配置不可用会报错，所以默认关闭，根据需要自行开启
ACCOUNT_EMAIL_VERIFICATION = os.getenv('IZONE_ACCOUNT_EMAIL_VERIFICATION', 'none')
# 登录方式，选择用户名或者邮箱都能登录
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
# 设置用户注册的时候必须填写邮箱地址
ACCOUNT_EMAIL_REQUIRED = True
# 登出直接退出，不用确认
ACCOUNT_LOGOUT_ON_GET = True

# 表单插件的配置
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'izone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 设置视图
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'blog.context_processors.settings_info',  # 自定义上下文管理器
            ],
        },
    },
]

WSGI_APPLICATION = 'izone.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False  # 关闭国际时间，不然数据库报错

# 统一分页设置
BASE_PAGE_BY = 10
BASE_ORPHANS = 3

# *************************************** 静态文件配置开始 ***************************************
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

# 静态文件收集
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 媒体文件收集
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# *************************************** 静态文件配置结束 ***************************************


# *************************************** 全文配置开始 ***************************************
# 全文搜索应用配置
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'blog.whoosh_cn_backend.WhooshEngine',  # 选择语言解析器为自己更换的结巴分词
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),  # 保存索引文件的地址，选择主目录下，这个会自动生成
    }
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# *************************************** 全文配置结束 ***************************************


# ************************************* restframework配置开始 **********************************
# restframework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20
}
# ********************************** restframework配置开始 ************************************


# *************************************** 数据库配置开始 ***************************************
# 配置数据库
izone_mysql_host = os.getenv('IZONE_MYSQL_HOST', '127.0.0.1')
izone_mysql_name = os.getenv('IZONE_MYSQL_NAME', 'izone')
izone_mysql_user = os.getenv('IZONE_MYSQL_USER', 'root')
izone_mysql_pwd = os.getenv('IZONE_MYSQL_PASSWORD', 'python')
izone_mysql_port = os.getenv('IZONE_MYSQL_PORT', 3306)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 修改数据库为MySQL，并进行配置
        'NAME': izone_mysql_name,  # 数据库的名称
        'USER': izone_mysql_user,  # 数据库的用户名
        'PASSWORD': izone_mysql_pwd,  # 数据库的密码
        'HOST': izone_mysql_host,
        'PORT': izone_mysql_port,
        'OPTIONS': {'charset': 'utf8mb4', 'use_unicode': True}
    }
}
# *************************************** 数据库配置结束 **************************************


# *************************************** 缓存配置开始 ***************************************
# 使用django-redis缓存页面，缓存配置如下：
izone_redis_host = os.getenv('IZONE_REDIS_HOST', '127.0.0.1')
izone_redis_port = os.getenv('IZONE_REDIS_PORT', 6379)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/0".format(izone_redis_host, izone_redis_port),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# *************************************** 缓存配置结束 ***************************************


# *************************************** celery 配置开始 ***************************************
# 跟缓存的redis配置类似，使用不同的库就行
CELERY_BROKER_URL = "redis://{}:{}/1".format(izone_redis_host, izone_redis_port)
# 时区跟Django的一致
CELERY_TIMEZONE = TIME_ZONE
# 不使用utc，所以在定时任务里面的时间应该比上海时间少8小时，比如要设置本地16:00执行，那么应该在定时里面设置成8:00
CELERY_ENABLE_UTC = False
# 应对django在使用mysql的时候设置USE_TZ = False导致的报错
DJANGO_CELERY_BEAT_TZ_AWARE = False
# 支持数据库django-db和缓存django-cache存储任务状态及结果
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = 'django-cache'
# 将任务调度器设为DatabaseScheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# celery内容等消息的格式设置，默认json
CELERY_ACCEPT_CONTENT = ['application/json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# 每个 worker 最多执行n个任务就会被销毁，可防止内存泄露
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
# 为存储结果设置过期日期，默认1天过期。如果beat开启，Celery每天会自动清除，0表示永不清理
# 这里可以设置成0，然后自己创建清理结果的机制，比较好控制
CELERY_RESULT_EXPIRES = 0
# *************************************** celery 配置结束 ***************************************


# ****************************************** 邮箱配置开始 ****************************************
# 配置管理邮箱，服务出现故障会收到到邮件，环境变量值的格式：name|test@test.com 多组用户用英文逗号隔开
ADMINS = []
admin_email_user = os.getenv('IZONE_ADMIN_EMAIL_USER')
if admin_email_user:
    for each in admin_email_user.split(','):
        a_user, a_email = each.split('|')
        ADMINS.append((a_user, a_email))

# 邮箱配置
EMAIL_HOST = os.getenv('IZONE_EMAIL_HOST', 'smtp.163.com')
EMAIL_HOST_USER = os.getenv('IZONE_EMAIL_HOST_USER', 'your-email-address')
EMAIL_HOST_PASSWORD = os.getenv('IZONE_EMAIL_HOST_PASSWORD',
                                'your-email-password')  # 这个不是邮箱密码，而是授权码
EMAIL_PORT = os.getenv('IZONE_EMAIL_PORT', 465)  # 由于阿里云的25端口打不开，所以必须使用SSL然后改用465端口
EMAIL_TIMEOUT = 5
# 是否使用了SSL 或者TLS，为了用465端口，要使用这个
EMAIL_USE_SSL = os.getenv('IZONE_EMAIL_USE_SSL', 'True').upper() == 'TRUE'
# 默认发件人，不设置的话django默认使用的webmaster@localhost，所以要设置成自己可用的邮箱
DEFAULT_FROM_EMAIL = os.getenv('IZONE_DEFAULT_FROM_EMAIL', 'TendCode博客 <your-email-address>')
# *************************************** 邮箱配置结束 *******************************************


# ***************************************** 网站配置开始 ****************************************
# 网站默认设置和上下文信息
SITE_LOGO_NAME = os.getenv('IZONE_LOGO_NAME', 'TendCode')
SITE_END_TITLE = os.getenv('IZONE_SITE_END_TITLE', 'izone')
SITE_DESCRIPTION = os.getenv('IZONE_SITE_DESCRIPTION', 'izone 是一个使用 Django+Bootstrap4 搭建的个人博客类型网站')
SITE_KEYWORDS = os.getenv('IZONE_SITE_KEYWORDS', 'izone,Django博客,个人博客')
# ***************************************** 网站配置结束 *****************************************


# ***************************************** 个性化配置开始 ****************************************
# 个性化设置，非必要信息
# 网站部署日期
SITE_CREATE_DATE = os.getenv('IZONE_SITE_CREATE_DATE', '2023-01-01')
# 个人 Github 地址
MY_GITHUB = os.getenv('IZONE_GITHUB', 'https://github.com/Hopetree')
# 工信部备案信息
BEIAN = os.getenv('IZONE_BEIAN', '网站备案信息')
# 站长统计（友盟）
CNZZ_PROTOCOL = os.getenv('IZONE_CNZZ_PROTOCOL', '')
# 站长统计（51.la）
LA51_PROTOCOL = os.getenv('IZONE_LA51_PROTOCOL', '')
# 站长推送
MY_SITE_VERIFICATION = os.getenv('IZONE_SITE_VERIFICATION', '')
# 使用 http 还是 https （sitemap 中的链接可以体现出来）
PROTOCOL_HTTPS = os.getenv('IZONE_PROTOCOL_HTTPS', 'HTTP').lower()
# 个人外链信息（导航栏下拉中显示）
PRIVATE_LINKS = os.getenv('IZONE_PRIVATE_LINKS', '[]')
# ***************************************** 个性化配置结束 ****************************************


# ****************************************** 日志配置开始 *****************************************
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'backupCount': 7,
            'filename': os.path.join(BASE_DIR, 'log', 'izone.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
    }
}
# ****************************************** 日志配置结束 *****************************************
