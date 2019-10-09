FROM python:3.6
ARG pip_url=http://pypi.douban.com/simple
ARG pip_host=pypi.douban.com
ARG work_home=/opt/cloud/izone
ENV PYTHONUNBUFFERED=1

# change repositories to aliyun and set timezone to Shanghai
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN mkdir -p ${work_home}
WORKDIR ${work_home}
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt -i ${pip_url} --trusted-host ${pip_host}
COPY . .
