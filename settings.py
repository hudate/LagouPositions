
import pymongo
import redis

proxy_redis_keys = {'proxy_url': 'proxy_url'}

lagou_redis_keys = {'lagou_url': 'lagou_url'}

redis_setting = redis.Redis(
    host='localhost',
    port=6379,
    password='123456',
    db=1
)

mongo_setting = {
    'host': 'localhost',
    'port': 27017,
    'db': 'ProxyInfo',
    'collection': 'proxy'
}

mysql_setting = {
    'host': 'localhost',
    'port': 3306,
    'user': 'position',
    'passwd': 'posi123456',
    'db': 'LagouPositions'
}


def set_mongo():
    mongo_client = pymongo.MongoClient(host=mongo_setting['host'], port=mongo_setting['port'])
    db = mongo_client[mongo_setting['db']]
    coll = db[mongo_setting['collection']]
    return coll

proxy_spider_delta_time = 10      # 设置爬虫爬取代理信息的时间间隔，单位：分钟
lagou_spider_delta_time = 10      # 设置爬虫爬取拉勾网信息的时间间隔，单位：分钟

