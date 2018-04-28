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
from core import config
from core import logger
from wxext.client import Client as WxExtClient

logger = logger.get('Manager')


class Manager(object):
    _client_command_consumer = None
    _clients = {}

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
        wxext.producer = self.statistic_consumer_factory('wxext')
        self._clients['wxext'] = wxext

    def start_statistic(self):
        for cname in self._clients:
            t = threading.Thread(target=self._clients[cname].statistic)
            t.start()

    def __init__(self):
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        logger.info('Start to connect kafka [%s]' % kafka_server)
        self._client_command_consumer = KafkaConsumer('agency.command',
                                                      client_id='agency_manager',
                                                      bootstrap_servers=kafka_server)
        # run initial clients automatically
        logger.info('Start to run default client...')
        self._run_default_client()
        logger.info('Start statistic...')
        self.start_statistic()

        # listen commands topic
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

    def _handle_command(self, commands, meta):
        '''
        :param commands:
        {
            "target": "client"
            "client": "wxext",
            "commands": [
                // details, parsed by the client
            ]
        }
        :param meta:
        :return:
        '''
        logger.info('Receive command: %r' % commands)
        if commands['target'] == 'client':
            if 'client' in commands and commands['client'] in self._clients:
                self._clients[commands['client']].perform(commands['commands'])
        elif commands['target'] == 'manager':
            pass
        pass


if __name__ == '__main__':
    manager = Manager()




