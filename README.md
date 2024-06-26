一个以 Django 作为框架搭建的个人博客。

博客效果： https://tendcode.com/

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
- 缓存系统，遵循缓存原则，加速网站打开速度
- RESTful API 风格的 API 接口

## 博客页面效果（响应式）
- PC 页面效果

![PC首页](https://github.com/Hopetree/izone/assets/30201215/e221d09b-9921-4707-977d-95c263d282b6)

- PC 暗色主题效果

![PC首页暗色主题](https://github.com/Hopetree/izone/assets/30201215/ca505bfc-e5d0-40a1-b501-946975c03f73)

- PC 文章详情页，左边显示专题目录，右边显示文章目录，支持代码高亮

![PC文章页面](https://github.com/Hopetree/izone/assets/30201215/0c219bbd-6f29-4866-a827-6e98536f689a)

- PC 专题页，按文章归类

![PC 专题页，按文章归类](https://github.com/Hopetree/izone/assets/30201215/c0a828cc-2201-438b-a983-0c6c04a429c4)

- 云监控服务，提供服务器的监控能力，客户端提供 Golang 版本，也可以自行编写 Python 版本的客户端用来上报数据

![20240404_232431 (1)](https://github.com/Hopetree/izone/assets/30201215/038200c3-1ada-4ab2-9ac5-42848a80ee21)

- PC 友情链接页，定时任务自动校验网址有效性

![PC 友情链接页](https://github.com/Hopetree/izone/assets/30201215/033cdd61-75cf-41b4-bb45-9b45948daf3a)

- PC 在线工具，平台自带工具

![PC 在线工具](https://github.com/Hopetree/izone/assets/30201215/8336fd89-916b-49e5-94f2-a5a72e990158)

- ipad 效果

![ipad](https://user-images.githubusercontent.com/30201215/60588800-7e558800-9dca-11e9-8beb-5d2dcf01b869.jpg)

- 手机效果

![iphone](https://user-images.githubusercontent.com/30201215/60588832-8e6d6780-9dca-11e9-84fa-f1d71510c81e.jpg)

## 运行指导
- 由于本项目分为几个不同的分支，每个分支的功能是一样的，但是运行的方式不同，所以需要根据分支查看对应的运行wiki
- 指导 wiki：https://github.com/Hopetree/izone/wiki