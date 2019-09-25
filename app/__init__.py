#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Flask
from app.middleware import load_middleware
from app.views import blue
from app.ext import app_init
from settings import mysql_setting


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s' % \
        (mysql_setting['user'], mysql_setting['passwd'], mysql_setting['host'], mysql_setting['db'])
    app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    load_middleware(app)
    app.register_blueprint(blue)
    app_init(app)
    return app