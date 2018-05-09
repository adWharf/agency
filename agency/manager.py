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
from exceptions import UnknowCommandException

logger = logger.get('Manager')

_available_clients = {
    'wxext': WxExtClient
}


class Manager(object):
    _client_command_consumer = None
    _clients = {}

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

    def statistic_consumer_factory(self, name):
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        return KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                             client_id='agency_client_'+name,
                             compression_type='gzip',
                             bootstrap_servers=kafka_server,
                             retries=3)

    def _run_default_client(self):
        wxext = WxExtClient()
        wxext.producer = self.statistic_consumer_factory('wxext')
        self._clients['wxext'] = wxext

    def start_statistic(self):
        for cname in self._clients:
            t = threading.Thread(target=self._clients[cname].statistic)
            t.start()

    def _handle_command(self, commands, meta):
        '''
        :param commands:
        {
            "target": "client"   // manager
            "client": "wxext",
            "commands": [
                // details, parsed by the client
            ]
        }
        :param meta:
        :return:
        '''
        try:
            logger.info('Receive command: %r' % commands)
            if commands['target'] == 'client':
                if 'client' in commands and commands['client'] in self._clients:
                    self._clients[commands['client']].perform(commands['commands'])

            elif commands['target'] == 'manager':
                for command in commands['commands']:
                    if command['type'] == 'operate_client':

                        if command['action'] == 'start':
                            if command['target'] in self._clients:
                                logger.notice('%s is already running...' % command['target'])
                            elif command['target'] in _available_clients:
                                self._clients[command['target']] = _available_clients[command['target']]()
                            else:
                                raise UnknowCommandException()
                        elif command['action'] == 'stop':
                            if command['target'] in self._clients:
                                rtn = self._clients[command['target']].quit()
                                logger.info('Stop [%s] with status [%s]' % (command['target'], rtn))
                            else:
                                logger.notice('[%s] is not running!' % command['target'])
                        elif command['action'] == 'restart':
                            if command['target'] in self._clients:
                                rtn = self._clients[command['target']].quit()
                                logger.info('Stop [%s] with status [%s]' % (command['target'], rtn))
                            self._clients[command['target']] = _available_clients[command['target']]()
                        else:
                            raise UnknowCommandException(command)
                    else:
                        raise UnknowCommandException(command)
                pass
            pass
        except UnknowCommandException as e:
            logger.error('Unknow command:')
            logger.error(e)
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    manager = Manager()




