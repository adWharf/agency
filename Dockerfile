FROM python:3.6.5-alpine3.7

MAINTAINER 1342247033@qq.com

ENV PYTHONPATH /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    apk --no-cache add tzdata  && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
COPY . .

EXPOSE 5000
VOLUME /usr/src/app/config

CMD [ "python", "agency/manager.py" ]
