# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from gevent import monkey, pywsgi
monkey.patch_all()  # 打上猴子补丁

import sys
sys.path.append('..')

from flask_script import Manager
from app.__init__ import create_app

app = create_app()
manager = Manager(app)

@manager.option('-p', '--port', help='Server Port')
def runserver_port(port):
    global server_port
    server_port = port

@manager.option('-h', '--host', help='Server Host')
def runserver_host(host):
    global server_host
    server_host = host

@manager.command
def runserver_gevent():
    server = pywsgi.WSGIServer((server_host, server_port), app)
    server.serve_forever()

if __name__ == "__main__":
    manager.run()
