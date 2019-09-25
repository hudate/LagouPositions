import time

from flask import request, g, jsonify


def load_middleware(app):
    @app.before_first_request
    def before_first_request():     # 第一次发起请求时执行
        print('first request')
        # return request

    @app.before_request     # 请求到达视图前执行
    def before_request():
        print('我在 before request')
        ban_UA_list = ['postman',
                    'python']
        for ban_UA in ban_UA_list:
            if ban_UA in request.headers['User-Agent'].lower():
                return jsonify({'code': 3000, 'msg': 'Wrong Browser!'})

        # print('time:%s, User-Agent:%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), request.headers[
        #     'User-Agent']))

        # return request

    @app.after_request      # 请求后执行，但是未发生异常或者异常被捕获
    def after_request(response):
        print('我到了 after request')
        return response

    @app.teardown_request       # 请求后执行，发生异常且异常被捕获
    def teardown(e):
        print('teardown request..., 原因:%s' % e)
        return e