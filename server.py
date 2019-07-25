#!/usr/bin/env python
# coding=utf-8
import os
import glob
import numpy as np
import json
from flask import Flask, request, render_template, redirect, url_for

from myresponse import DataResponse


class FlaskAppWrapper(object):
    app = None

    def __init__(self, name):
        self.app = Flask(name, static_url_path='/static')

    def run(self, **kwargs):
        self.app.run(**kwargs)

    def add_endpoint(self,
                     endpoint=None,
                     endpoint_name=None,
                     handler=None,
                     **kwargs):
        self.app.add_url_rule(endpoint, endpoint_name, handler, **kwargs)


class Page(object):
    def __init__(self, conf_path):
        self.path = conf_path

    def work(self):
        return render_template('work.html')

    def conf(self):
        return render_template('conf.html')

    def login(self):
        return render_template('login.html')

if __name__ == "__main__":
    page = Page('configure.json')

    a = FlaskAppWrapper('wrap')
    dr = DataResponse()
    a.add_endpoint(endpoint='/', endpoint_name='login', handler=page.login)
    a.add_endpoint(endpoint='/conf', endpoint_name='conf', handler=page.conf)
    a.add_endpoint(endpoint='/work', endpoint_name='work', handler=page.work)

    a.add_endpoint(endpoint='/login/backend',
                   endpoint_name='login_',
                   handler=dr.login,
                   methods=['POST', 'GET'])
    a.add_endpoint(endpoint='/conf/configure',
                   endpoint_name='configure',
                   handler=dr._configure,
                   methods=['POST', 'GET'])
    a.add_endpoint(endpoint='/finish',
                   endpoint_name='finish',
                   handler=dr.page_finish)
    a.add_endpoint(endpoint='/get',
                   endpoint_name='get',
                   handler=dr,
                   methods=['POST', 'GET'])
    a.add_endpoint(endpoint='/work/save',
                   endpoint_name='save',
                   handler=dr.autosave)

#   a.run(host='0.0.0.0', port=10299)
    a.run()
