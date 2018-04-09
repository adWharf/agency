#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: bridge.py
@time: 08/04/2018 15:54
"""

import json
from multiprocessing import Pipe
from flask import Flask, request
from core import config


_bridge = Flask(__name__)
global _data_q  # type: Pipe
global _command_q  # type: Pipe


def set_client(ct):
    global client
    client = ct


@_bridge.route('/dataReporters', methods=['POST'])
def data_reporters():
    global _command_q, _data_q
    res = json.loads(request.form['data'])
    _data_q.send(res)
    commands = []
    if _command_q.poll():
        commands = _command_q.rece()
    return json.dumps({
        'stats': 'ok',
        'commands': commands
    })


def run(data_q: Pipe, command_q: Pipe):
    global _data_q, _command_q
    _data_q = data_q
    _command_q = command_q
    _bridge.run(host='0.0.0.0', port=config.get('app.clients.wxext.bridge.port'))
