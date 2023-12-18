FROM python:3.9
ARG pip_index_url=https://pypi.org/simple
ARG pip_trusted_host=pypi.org
ENV PYTHONUNBUFFERED=1
WORKDIR /opt/cloud/izone

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --index-url $pip_index_url --trusted-host $pip_trusted_host
RUN mkdir -p log && chmod -R 755 log

COPY . .

# 设置镜像的创建时间，当做网站更新时间
RUN sed -i "s/web_update_time=\"\"/web_update_time=\"$(date +'%Y-%m-%d %H:%M')\"/g" ./apps/blog/templates/blog/base.html

CMD ["supervisord", "-n", "-c", "supervisord.conf"]
