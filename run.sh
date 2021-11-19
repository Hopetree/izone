#!/bin/bash
# 项目目录
workdir=$(cd $(dirname $0); pwd)
# 网络类型 http、socket
net_type=$1
# 静态文件目录
static_blog_path="$workdir/static/blog"

# 刷新环境变量 此方案容器重启也可刷新变量
# 提前将自己的environment挂载到/etc/environment
source /etc/environment
# 初始化数据
python manage.py makemigrations
python manage.py migrate
# 初始化搜索索引
python manage.py update_index

# 创建django超级用户
CreateSuperUser(){
  # user email password
  echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
  User.objects.create_superuser('$1', '$2', '$3')" | python manage.py shell && echo 'Superuser created successfully.'
}

# 创建Django超级用户操作,先判断静态文件目录是否存在不存在则创建
if [ ! -d "$static_blog_path" ]; then
  echo "******The ($static_blog_path) directory does not exist. Create a superuser!******"
  # 提前设置环境变量$DJANGO_SUPERUSER_PASSWORD、$DJANGO_SUPERUSER_USER、$DJANGO_SUPERUSER_EMAIL
  if [ ! $DJANGO_SUPERUSER_PASSWORD ];then
    echo "******The Environment variable value of (DJANGO_SUPERUSER_PASSWORD) does not exist. You do not need \
to create a superuser!******"
  else
    if [ ! $DJANGO_SUPERUSER_EMAIL ];then
      if [ ! $DJANGO_SUPERUSER_USER ];then
        echo "******The (DJANGO_SUPERUSER_USER and DJANGO_SUPERUSER_EMAIL) Environment variable values do not \
exist and the default values (admin and admin@163.com) are used to create the superuser!******"
        [ $DJANGO_SUPERUSER_PASSWORD ] && CreateSuperUser admin admin@163.com $DJANGO_SUPERUSER_PASSWORD
        # 此方案创建user无法登录,弃用
        # && python manage.py createsuperuser --noinput --username  admin  --email admin@163.com

      else
        echo "******The (DJANGO_SUPERUSER_EMAIL) Environment variable value does not exist, use the default \
(admin@163.com) to create the superuser!******"
        [ $DJANGO_SUPERUSER_PASSWORD ] \
        && [ $DJANGO_SUPERUSER_USER ] && CreateSuperUser $DJANGO_SUPERUSER_USER admin@163.com $DJANGO_SUPERUSER_PASSWORD
        # && python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USER  --email admin@163.com

      fi
    else
      echo "******(DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_USER, DJANGO_SUPERUSER_EMAIL) Environment variable \
values exist and are used to create the superuser!******"
      [ $DJANGO_SUPERUSER_PASSWORD ] \
      && [ $DJANGO_SUPERUSER_USER ] \
      && [ $DJANGO_SUPERUSER_EMAIL ] && CreateSuperUser $DJANGO_SUPERUSER_USER $DJANGO_SUPERUSER_EMAIL $DJANGO_SUPERUSER_PASSWORD
      # && python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USER  --email $DJANGO_SUPERUSER_EMAIL

    fi
  fi
else
  echo "******The ($static_blog_path) directory already exists and is not the first run. You do not need to create \
a superuser!******"
fi
# 收集静态文件
printf 'yes\n' | python manage.py collectstatic
# 启动nginx
service nginx restart
# 启动uwsgi服务
uwsgi --ini uwsgi-$net_type.ini
