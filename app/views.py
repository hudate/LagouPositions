from urllib import parse
from flask import Blueprint, jsonify, request
from settings import set_mongo
import random

blue = Blueprint('blue', __name__)
mongo = set_mongo()


@blue.route('/api/v1/proxy', methods=['GET'])
def get_proxy():
    query_str = {e_t[0]: e_t[1] for e_t in parse.parse_qsl(str(request.query_string, encoding='utf-8'))}
    if 'type' not in query_str.keys():
        return jsonify({'code': 4000, 'msg': '请求参数有误！'})
    if 'https' not in query_str.values() and 'http' not in query_str.values():
        return jsonify({'code': 4001, 'msg': '请求参数的值有误！'})
    query_type = query_str['type']
    find_dict = {'type': query_type.upper()}
    try:
        proxy = mongo.find_one(find_dict, {'_id': 0, 'type': 0})
        proxy_ip = proxy['ip']
        proxy_port = proxy['port']
        result = {query_type.lower(): query_type.lower() + "://" + proxy_ip + ':' + proxy_port}
        return jsonify(result)
    except:
        return jsonify({'code': 4002, 'msg': '服务器出错！'})


@blue.route('/api/v1/proxies', methods=['GET'])
def get_many_proxy():
    query_str = {e_t[0]: e_t[1] for e_t in parse.parse_qsl(str(request.query_string, encoding='utf-8'))}
    query_count = query_str['count']
    query_type = query_str['type']
    find_dict = {'type': query_type.upper()}
    proxies = [{query_type.lower(): query_type.lower() + "://" + proxy['ip'] + ':' + proxy['port']} for proxy in
              mongo.find_one(find_dict, {'_id': 0})]
    result = set()
    while len(result) < query_count:
        result.add(random.choice(proxies))
    result = list(result)
    return jsonify(result)





