FROM python:3.8
ARG work_home=/opt/izone
ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 TZ=Asia/Shanghai LANG=C.UTF-8

RUN sed -i s@/security.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
&& sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
# change repositories to aliyun and set timezone to Shanghai
&& cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
&& mkdir -p ~/.pip/ \
&& echo "[global]\nindex-url = http://mirrors.aliyun.com/pypi/simple \
\n[install]\ntrusted-host=mirrors.aliyun.com" > ~/.pip/pip.conf \
# Installation tools
&& apt-get update \
&& apt-get install -y wget vim curl nginx \
&& apt-get clean \
&& rm -rf /var/cache/apk/* \
&& rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${work_home}
WORKDIR ${work_home}
RUN git clone https://hub.fastgit.org/LoganJinDev/izone.git ${work_home} \
&& cd ${work_home} && pip install -r requirements.txt \
&& pip install uwsgi

