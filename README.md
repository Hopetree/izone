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

### 版本说明及安装说明
博客目前有两个主要的版本，分别是分支[feature/1.0](https://github.com/Hopetree/izone/tree/feature/1.0)，和分支[feature/2.0](https://github.com/Hopetree/izone/tree/feature/2.0)。两个版本的博客功能完全一致，区别仅仅是1.0版本将数据库设置成默认的数据库，安装运行的时候不需要单独安装和配置MySQL，同时将缓存数据库也设置成一个python的第三方库，不再依赖于redis，所以也不需要安装配置redis数据库。因此，如果想要更快捷的运行本博客项目，可以支持查看feature/1.0分支的安装运行说明，如果想要使用以上提到的两个数据库，则取查看feature/2.0的使用说明即可。

### 作者声明
有任何关于博客的想法或者疑问可以取博客相关文章下评论，有博客代码相关问题可以在项目中提交issues

PS：请各位使用了我的博客的源码或者直接参考我的博客源码改写成自己的博客的同学能够尊重我的成果，在您的网址上线之后能够给一个链接指向我的Github，写明您的博客主要支持的来源是我的Github博客项目，谢谢！