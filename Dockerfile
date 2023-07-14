FROM python:3.9
ARG pip_index_url=https://pypi.org/simple
ARG pip_trusted_host=pypi.org
ENV PYTHONUNBUFFERED=1
WORKDIR /opt/cloud/izone

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && mkdir -p log && chmod -R 755 log
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --index-url $pip_index_url --trusted-host $pip_trusted_host
COPY . .

CMD ["supervisord", "-n", "-c", "supervisord.conf"]
