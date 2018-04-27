FROM python:3.6.5-alpine3.7
WORKDIR /usr/src/app
EXPOSE 5000
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    ln -s /usr/src/app/agency /usr/local/lib/python3.6/site-packages/
COPY . .
CMD [ "python", "agency/manager.py" ]
