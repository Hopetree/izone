FROM python:3.9
ENV PYTHONUNBUFFERED=1
WORKDIR /opt/cloud/izone

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
