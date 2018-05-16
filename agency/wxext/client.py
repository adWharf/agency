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
from multiprocessing import Process, Pipe
from agency.client import APIClient, Account as BaseAccount
from .bridge import run as build_bridge, TYPE_STATISTIC, TYPE_CAMP_INFO, TYPE_ACTION_RES
from agency.core import logger

AD_CAMPAIGN_INFO_TOPIC = 'ad.campaign.info'             # 投放计划信息

logger = logger.get('Wxext.Client')


class Account(BaseAccount):
    pass


class Client(APIClient):

    _agency = 'wxext'

    def __init__(self, account=None):
        APIClient.__init__(self, account)
        self._data_q, another_data_end = Pipe()
        self._command_q, another_command_end = Pipe()
        # start server to receive data from wx-retinue
        self._bridge = Process(target=build_bridge, args=(another_data_end, another_command_end))
        self._bridge.start()

    def perform(self, commands):
        '''
        :param commands:
        [
            {
                "campaign_id": 1
                "action": "suspend",
                "value": None
            },
            {
                "campaign_id": 2
                "action": "timeset_end",
                "value": 6
            }
        ]
        :return:
        '''
        self._command_q.send(commands)

    @staticmethod
    def transformer(original_data):
        rtn = {
            'agency': 'wxext'
        }
        reversed_keys = ['total_cost', 'view_count', 'sy_cost', 'update_time', 'cname']
        map_key = {
            'cid': 'campaign_id',
        }
        # rtn['update_time'] = pendulum.from_format(original_data['update_time'], '%Y%m%d%H%M').to_datetime_string()
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
                try:
                    data = str(self._data_q.recv_bytes(), encoding='utf-8')
                    resp = json.loads(data)

                    if resp['type'] == TYPE_CAMP_INFO:
                        '''
                        Report campaign info
                        '''
                        logger.info('Receive campaigns info')
                        self._producer.send(AD_CAMPAIGN_INFO_TOPIC, {
                            'agency': self._agency,
                            'account': resp['data']['account'],
                            'campaigns': json.loads(resp['data']['campaigns']),
                        })
                        logger.info('Send campaign data to kafka successfully')
                    elif resp['type'] == TYPE_ACTION_RES:
                        '''
                        Report action result
                        {
                            id: 1,
                            resp_cnt: 'success',
                            resp_status: 200
                        }
                        '''
                        logger.info('Receive action perform results')
                        data = resp['data']
                        self.report_perform_res(data['id'], data['resp_cnt'], data['resp_status'])
                        logger.info('Send action results to kafka successfully')

                    elif resp['type'] == TYPE_STATISTIC:
                        ''''
                        Report statistic
                        {
                            data: [
                                {},
                                {}
                            ],
                            account: 'myaccount',
                            'update_hour: '201804151005'
                        }
                        '''
                        resp = resp['data']
                        logger.info('Receive statistic info')
                        processed_data = []
                        update_at = pendulum.from_format(resp['update_hour'], '%Y%m%d%H%M').to_datetime_string()
                        for record in resp['data']:
                            record['update_time'] = update_at
                            record['account'] = resp['account']
                            processed_data.append(self.transformer(record))
                        self.producer.send(self._statistic_topic, {
                            'data': processed_data,
                            'update_time': update_at,
                            'account': resp['account']})
                        logger.info('Send ad data to kafka successfully')
                except Exception as e:
                    logger.error('Exception raised when send data to kafka')
                    logger.error(e)
            time.sleep(5)

    def quit(self):
        self._bridge.terminate()

