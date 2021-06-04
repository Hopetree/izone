FROM python:3.6
ARG pip_url=https://pypi.tuna.tsinghua.edu.cn/simple
ARG pip_host=https://pypi.tuna.tsinghua.edu.cn
ARG work_home=/opt/cloud/izone
ENV PYTHONUNBUFFERED=1

# change repositories to aliyun and set timezone to Shanghai
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN mkdir -p ${work_home}
WORKDIR ${work_home}
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt -i ${pip_url} --trusted-host ${pip_host}
COPY . .
