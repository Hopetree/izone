一个以 Django 作为框架搭建的个人博客。

博客主页 http://www.tendcode.com/

## 关于网站
- 本网站是一个个人博客网站，主要分享博主的编程学习心得
- 网站主要使用 Django + Bootstrap4 搭建，源码在博主 Github 中， 目前部署在阿里云 ECS
- 我的目的是让这个博客网站不仅仅是一个博客，所以会尽己所能持续扩展网站的功能


## 功能介绍
- Django 自带的后台管理系统，方便对于文章、用户及其他动态内容的管理
- 文章分类、标签、浏览量统计以及规范的 SEO 设置
- 用户认证系统，在 Django 自带的用户系统的基础上扩展 Oauth 认证，支持微博、Github 等第三方认证
- 文章评论系统，炫酷的输入框特效，支持 markdown 语法，二级评论结构和回复功能
- 信息提醒功能，登录和退出提醒，收到评论和回复提醒，信息管理
- 强大的全文搜索功能，只需要输入关键词就能展现全站与之关联的文章
- RSS 博客订阅功能及规范的 Sitemap 网站地图
- 实用的在线工具
- 友情链接和推荐工具网站的展示
- django-redis 支持的缓存系统，遵循缓存原则，加速网站打开速度
- RESTful API 风格的 API 接口

## 网站支持
- 前端使用 Bootstrap4 + jQuery 支持响应式；图标使用 Font Awesome
- 后端 Python 3.5.2，Django 1.11.12，其他依赖查看源码中 requirements.txt
- 数据库使用 MySQL
- 网站部署使用的 Nginx + gunicorn
- bootstrap-admin 用于美化后台管理系统，变成响应式界面
- django-allauth 等用于第三方用户登录
- django-haystack 和 jieba 用于支持全文搜索
- redis 支持缓存
- django restframework 提供 API 接口
- 其他依赖查看网站源码解释


## 博客主页效果
![博客主页 PC 效果](https://user-images.githubusercontent.com/30201215/39048724-0ad6e930-44d1-11e8-83f0-661734ddbde4.png)

## 博客手机端显示效果（响应式）
![博客手机端效果](https://user-images.githubusercontent.com/30201215/39047823-e7daccb0-44cd-11e8-9851-5aa670a8a690.png)

## 使用步骤：

### 必须的支持项
- Python3.4 以上
- redis 服务启动了，因为2018-4-18增加了django-redis缓存，所以必须要有redis了
- MySQL
- 其他依赖看依赖文件即可


### 克隆项目到本地
使用如下命令讲项目克隆到本地：
```
git clone git@github.com:Hopetree/izone.git
```

### 创建网站关键信息文件
由于涉及到网站的一些隐私信息，所以这个项目有一个文件没有上传到Github中，所以要在克隆项目之后自己创建这个文件。
在settings.py文件所在的文件夹下创建一个base_settings.py文件，然后在里面写入如下代码：
```
# -*- coding: utf-8 -*-
# 配置数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 修改数据库为MySQL，并进行配置
        'NAME': 'izone',
        'USER': 'root',
        'PASSWORD': 'python',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'OPTIONS': {'charset': 'utf8mb4', }
    }
}
# 邮箱配置
EMAIL_HOST = 'smtp.163.com'
EMAIL_HOST_USER = 'your-email@163.com'
EMAIL_HOST_PASSWORD = 'your-password'  # 这个不是邮箱密码，而是授权码
EMAIL_PORT = 465  # 由于阿里云的25端口打不开，所以必须使用SSL然后改用465端口
# 是否使用了SSL 或者TLS，为了用465端口，要使用这个
EMAIL_USE_SSL = True
# 默认发件人，不设置的话django默认使用的webmaster@localhost，所以要设置成自己可用的邮箱
DEFAULT_FROM_EMAIL = 'your-webname <your-email@163.com>'

# 网站默认设置和上下文信息
SITE_END_TITLE = '网站的名称，如TendCode'
SITE_DESCRIPTION = '网站描述'
SITE_KEYWORDS = '网站关键词，多个词用英文逗号隔开'
```

### 在虚拟环境中安装依赖
本项目的依赖文件可以在项目根目录看到，如何安装依赖可以查看我博客文章 http://www.seoerzone.com/article/virtualenv-for-python/

### 创建数据库

首先在自己的电脑上面创建一个数据库，根据配置信息里面填写的数据库信息去创建。比如数据库的名字为izone,那么我建议你使用下面这段MySQL的语句，注意，创建的数据库的编码格式是utf8mb4，原因是我的博客中支持emoji表情，所以必须使用这个格式才行：
```
CREATE DATABASE `izone` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 在虚拟环境中运行项目
首先要创建数据库表格，命令是：
```
(izone_env) F:\DjangoSpace\izone>python manage.py makemigrations
```
然后确认迁移：
```
(izone_env) F:\DjangoSpace\izone>python manage.py migrate
```
然后运行程序
```
(izone_env) F:\DjangoSpace\izone>python manage.py runserver --settings=izone.settings_dev
```

### 打开浏览器查看项目运行效果
在浏览器中输入 http://127.0.0.1:8000/ 即可查看项目的运行效果

### 要进入后台的话，需要先创建一个超级管理员账号:
```
(izone_env) F:\DjangoSpace\izone>python manage.py createsuperuser
```

有任何问题可以去博客的博客留言或者提交issues

PS：请各位使用了我的博客的源码或者直接参考我的博客源码改写成自己的博客的同学能够尊重我的成果，在您的网址上线之后能够给一个链接指向我的Github，写明您的博客主要支持的来源是我的Github博客项目，谢谢！