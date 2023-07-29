FROM python:3.9
ARG pip_index_url=https://pypi.org/simple
ARG pip_trusted_host=pypi.org
ENV PYTHONUNBUFFERED=1
WORKDIR /opt/cloud/izone

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --index-url $pip_index_url --trusted-host $pip_trusted_host
RUN mkdir -p log && chmod -R 755 log
RUN pip install django-webstack>=1.5.3 --index-url https://pypi.org/simple --trusted-host pypi.org

COPY . .

CMD ["supervisord", "-n", "-c", "supervisord.conf"]
