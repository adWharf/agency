#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: client.py
@time: 08/04/2018 15:34
"""
import pendulum
import time
import json
import threading
from multiprocessing import Process, Pipe
from client import APIClient, Account as BaseAccount
from .bridge import run as build_bridge
from core import logger


class Account(BaseAccount):
    pass


class Client(APIClient):

    def __init__(self, account=None):
        APIClient.__init__(self, account)
        self._data_q, another_data_end = Pipe()
        self._command_q, another_command_end = Pipe()
        # start server to receive data from wx-retinue
        bridge = Process(target=build_bridge, args=(another_data_end, another_command_end))
        bridge.start()

    def perform(self, commands):
        '''
        :param commands:
        [
            {
                "action": "STOP",
                ""
            }
        ]
        :return:
        '''
        for command in commands:
            self._command_q.send(command)

    @staticmethod
    def transformer(original_data):
        rtn = {}
        reversed_keys = ['total_cost', 'view_count', 'sy_cost']
        map_key = {
            'cid': 'campaign_id',
        }
        rtn['update_time'] = pendulum.from_format(original_data['update_hour'], '%Y%m%d%H%M').to_datetime_string()
        for key in reversed_keys:
            rtn[key] = original_data[key]
        for key in map_key:
            rtn[map_key[key]] = original_data[key]
        rtn['click_count'] = original_data['click_url_count'] + original_data['click_pic_count']
        if original_data['real_status'] == '投放中':
            rtn['status'] = 0
        elif original_data['real_status'] == '暂停投放':
            rtn['status'] = 4
        else:
            rtn['status'] = -1
        return rtn

    def statistic(self):
        while True:
            while self._data_q.poll():
                logger.info('Receive ad data')
                data = str(self._data_q.recv_bytes(), encoding='utf-8')
                resp = json.loads(data)
                processed_data = []
                for record in resp['camp_list']:
                    record['update_hour'] = resp['update_hour']
                    processed_data.append(self.transformer(record))
                self.producer.send(self._statistic_topic, data)
                logger.info('Send ad data to kafka successfully')
            time.sleep(5)
