FROM python:3.9
ARG work_home=/opt/cloud/izone
ENV PYTHONUNBUFFERED=1

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN mkdir -p ${work_home}
WORKDIR ${work_home}
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
