#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: exceptions.py
@time: 02/05/2018 12:10
"""
import json


class UnknowCommandException(Exception):
    def __init__(self, command):
        self._command = command

    def __str__(self):
        return json.dumps(self._command)

    def __repr__(self):
        return self.__str__(self)
