FROM python:3.6-alpine
ARG yum_repo=https://mirrors.aliyun.com/
ARG pip_url=http://pypi.douban.com/simple
ARG pip_host=pypi.douban.com
ARG work_home=/opt/cloud/izone
ENV PYTHONUNBUFFERED=1

# change repositories to aliyun and set timezone to Shanghai
RUN cp -a /etc/apk/repositories /etc/apk/repositories.bak \
    && sed -i "s@http://dl-cdn.alpinelinux.org/@${yum_repo}@g" /etc/apk/repositories \
    && apk add --no-cache --virtual .build-deps \
        jpeg-dev \
        zlib-dev \
        gcc \
        python3-dev \
        libc-dev \
        tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN mkdir -p ${work_home}
WORKDIR ${work_home}
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt -i ${pip_url} --trusted-host ${pip_host}
COPY . .
