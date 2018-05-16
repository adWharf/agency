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
import multiprocessing
from werkzeug.datastructures import Headers
from flask import Flask, request, Response as BaseResponse
from core import config


class Response(BaseResponse):
    def __init__(self, response=None, **kwargs):
        kwargs['headers'] = ''
        headers = kwargs.get('headers')
        origin = ('Access-Control-Allow-Origin', '*')
        methods = ('Access-Control-Allow-Methods', 'HEAD, OPTIONS, GET, POST, DELETE, PUT')
        extra = ('Access-Control-Allow-Headers', '*')
        if headers:
            headers.add(*origin)
            headers.add(*methods)
            headers.add(*extra)
        else:
            headers = Headers([origin, methods, extra])
        kwargs['headers'] = headers
        super().__init__(response, **kwargs)


_bridge = Flask(__name__)
_bridge.response_class = Response
global _data_q  # type: multiprocessing.Connection
global _command_q  # type: multiprocessing.Connection

TYPE_STATISTIC = 1
TYPE_CAMP_INFO = 2
TYPE_ACTION_RES = 3


def set_client(ct):
    global client
    client = ct


@_bridge.route('/dataReporters', methods=['POST'])
def data_reporters():
    '''
    request:
    {
        "data":{
                "camp_list":[{
                    "cid": 1636943340,
                    "total_budget": 3000000,
                    "total_cost": 16748,
                    "view_count": 2056,
                    "click_url_count": 3,
                    "click_pic_count": 31,
                    "heart_count": 3,
                    "comment_count": 0,
                    "click_follow_count": 0,
                    "share_timeline_action_count": 0,
                    "share_friend_action_count": 0,
                    "down_done_count": 0,
                    "down_click_count": 0,
                    "install_done_count": 0,
                    "install_click_count": 0,
                    "video_play_count": 0,
                    "video_share_count": 0,
                    "video_fav_count": 0,
                    "card_get_count": 0,
                    "card_use_count": 0,
                    "snsid": "12781723875482146681",
                    "real_status": "投放中",
                    "cname": "wechat_lgkj_414b-j",
                    "conv_index": "下单量：0",
                    "conv_rate": "0",
                    "conv_price": "0",
                    "date": "20180416",
                    "beg_date": "20180415",
                    "end_date": "20180514",
                    "detail_rate": "0.00145914",
                    "buy_type": "竞价购买",
                    "ad_type": "图文广告",
                    "tmpl_type": "电商推广",
                    "sy_cost": "167.48",
                    "sy_budget": "30000元/天",
                    "poi_pv": 0,
                    "ios_activated": 0,
                    "canvas_exp_pv": 35,
                    "canvas_sharefeed_pv": 0,
                    "canvas_sharecontact_pv": 0,
                    "canvas_fav_pv": 0,
                    "canvas_flag": "100",
                    "poi_uv": 0,
                    "order_pv": 0,
                    "order_amount": 0,
                    "quest_reservation_pv": 0
                }
            }
        ],
        "update_hour": "201804161735",
        "account": "广告投放账户"
    }
    :return:
    '''
    global _command_q, _data_q
    request_data = json.loads(request.form['data'])
    data = json.dumps({
        'type': TYPE_STATISTIC,
        'data': {
            'data': request_data['camp_list'],
            'account': request.form['account'],
            'update_hour': request_data['update_hour']
        }})
    _data_q.send_bytes(bytes(data, encoding='utf-8'))
    commands = []
    while _command_q.poll():
        commands += _command_q.recv()
        # At most 20 commands at one time
        if len(commands) > 20:
            break
    return json.dumps({
        'stats': 'ok',
        'commands': commands
    })


@_bridge.route('/campaigns', methods=['POST'])
def campaign_info_reporters():
    '''
    {
        'campaigns': [
            { // campaign1 },
            { // campaign2 }
        ],
        'account': 'my account'
    }
    :return:
    '''
    global _data_q
    data = json.dumps({
        'type': TYPE_CAMP_INFO,
        'data': {
            'campaigns': request.form['campaigns'],
            'account': request.form['account']
        }
    })
    _data_q.send_bytes(bytes(data, encoding='utf-8'))
    return json.dumps({
        'status': 'ok',
        'commands': []
    })


@_bridge.route('/actions/<id>', methods=['PUT'])
def action_result(id):
    _data_q.send_bytes(bytes(json.dumps({
        'type': TYPE_ACTION_RES,
        'data': {
            'id': id,
            'resp_cnt': request.form['resp_cnt'],
            'resp_status': request.form['resp_status']
        }
    }), encoding='utf-8'))
    return json.dumps({
        'status': 'ok',
        'commands': []
    })


def run(data_q, command_q):
    global _data_q, _command_q
    _data_q = data_q
    _command_q = command_q
    _bridge.run(host='0.0.0.0', port=config.get('app.clients.wxext.bridge.port'))
