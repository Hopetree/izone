一个以 Django 作为框架搭建的个人博客。

博客主页 www.seoerzone.com

博客主要功能：
- 用户认证
- 文章分类、标签云、文章内容页
- 文章评论、回复、被@之后收到信息推送通知
- 全文搜索功能
- RSS博客订阅
- 网站地图
- 实用工具

主要特点：
- 前端采用bootstrap4 ，博客完全响应式
- 文章内容采用markdown语法支持，简洁明了
- 博客支持emoji表情
- 评论采用ajax提交，被人@之后收到网页提醒和信息推送
- 由haystack和jieba分词支持的强大的全文搜索功能
- 用户认证支持第三方账号（微博、Github）登录

## 博客主页效果
![博客主页](http://cdn.seoerzone.com/article/180321/seoerzone-01.png)

## 博客文章页效果
![博客文章页](http://cdn.seoerzone.com/article/180321/seoerzone-03.png)

## 博客工具页面效果
![博客工具页面](http://cdn.seoerzone.com/article/180321/seoerzone-02.png)

## 博客后台效果
![博客后台页面](http://cdn.seoerzone.com/article/180321/seoerzone-admin.png)

## 博客Timeline页面
![博客TIMELINE](http://cdn.seoerzone.com/article/180321/seoerzone-timeline.png)

## 博客手机端显示效果（响应式）
![博客手机端效果](http://cdn.seoerzone.com/article/180321/seoerzone-m.png)

## 使用步骤：

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
DEFAULT_IMG_LINL = '一个默认的图片地址，用来给文章添加默认图片'
SITE_END_TITLE = '网站的名称，如SEO空间'
SITE_DESCRIPTION = '网站描述'
SITE_KEYWORDS = '网站关键词，多个词用英文逗号隔开'
```

### 在虚拟环境中安装依赖
本项目的依赖文件可以在项目根目录看到，如何安装依赖可以查看我博客文章 http://www.seoerzone.com/article/virtualenv-for-python/

### 创建数据库
在自己的MySQL中创建一个数据,根据自己的数据信息去更改项目的setting.py文件中的信息：
```
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

有任何问题可以去博客的博客留言