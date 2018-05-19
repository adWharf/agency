#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: http.py
@time: 19/05/2018 12:49
"""
import functools
from kafka import KafkaConsumer
from agency.core import config, logger

logger = logger.get('HTTP')


def route(topic, client, group=None):
    kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
    consumer = KafkaConsumer(topic,
                             client_id=client,
                             group_id=group,
                             bootstrap_servers=kafka_server)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for msg in consumer:
                try:
                    logger.info('Receive data from kafka for cunsumer [%s]' % client)
                    kwargs['message'] = msg
                    func(*args, **kwargs)
                except Exception as e:
                    logger.error('Err when handle data')
                    logger.error(e)
                    pass
        return wrapper
    return decorator
