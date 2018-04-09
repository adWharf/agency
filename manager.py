#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: manager.py
@time: 05/04/2018 23:08
"""
import threading
import json
from kafka import KafkaProducer, KafkaConsumer
from core import config, logger
from wxext.client import Client as WxExtClient


class Manager(object):
    _client_command_consumer = None
    _clients = {}

    @staticmethod
    def statistic_consumer_factory(self, name):
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        return KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                             client_id='agency_client_'+name,
                             compression_type='gzip',
                             bootstrap_servers=kafka_server,
                             retries=3)

    @logger.log
    def _run_default_client(self):
        wxext = WxExtClient()
        wxext.producer = self.statistic_consumer_factory(self, 'wxext')
        self._clients['wxext'] = wxext

    def start_statistic(self):
        for c in self._clients:
            t = threading.Thread(target=c.statistic)
            t.start()

    def __init__(self):
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        logger.info('Start to connect kafka [%s]' % kafka_server)
        self._client_command_consumer = KafkaConsumer('agency.action',
                                                      client_id='agency_manager',
                                                      bootstrap_servers=kafka_server)
        self._run_default_client()

        for record in self._client_command_consumer:
            try:
                logger.info(record)
                v = record.value
                if isinstance(v, bytes):
                    v = bytes.decode(v)
                self._handle_command(json.loads(v), record)
            except Exception as e:
                logger.error(e)
                pass

    def _handle_command(self, command, meta):
        # TODO handle action
        logger.info('Receive command: %r' % command)
        pass


if __name__ == '__main__':
    manager = Manager()




