#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: client.py
@time: 08/04/2018 15:34
"""
import time
import threading
from multiprocessing import Process, Pipe
from client import APIClient, Account as BaseAccount
from .bridge import run as build_bridge


class Account(BaseAccount):
    pass


class Client(APIClient):
    _enable_statistic = False
    _ready_commands = []

    def __init__(self, account=None):
        APIClient.__init__(self, account)
        self._data_q, another_data_end = Pipe()
        self._command_q, another_command_end = Pipe()
        bridge = Process(target=build_bridge, args=(another_data_end, another_command_end))
        bridge.start()

    def statistic(self):
        while True:
            if self._data_q.poll():
                data = self._data_q.recv()
                # TODO handle data
                self.producer.send(self._statistic_topic, data)
            time.sleep(60)
