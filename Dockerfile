FROM python:3.6.5-alpine3.7
ENV PYTHONPATH /usr/src/app
WORKDIR /usr/src/app
EXPOSE 5000
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    apk --no-cache add tzdata  && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
COPY . .
CMD [ "python", "agency/manager.py" ]
