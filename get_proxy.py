#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import time

sys.path.append('..')

import datetime
from settings import *

need_modules = ["requests", "lxml", "csv", "pymongo"]
you_need_modules = []

for module in need_modules:
    try:
        __import__(module)
    except:
        you_need_modules.append(module)

if len(you_need_modules) != 0:
    print("你需要安装库：%s" % you_need_modules)
    print("你可以使用: pip install %s 来安装你所需要的库。" % str(you_need_modules).replace("', '", ' ')[2:-2])
else:
    print('开始获取代理IP......')

import requests
from lxml import etree
import csv
import random
import redis
import telnetlib

class GetProxy(object):
    """ 获取代理IP，包括国内的和国外的。"""

    def __init__(self, writeproxy=False, *args, **kwargs):

        """
            self.__getIP_ip: 获取代理IP的网址，
            self.__filename: 保存代理IP，
            self.__writeInfo: 设置是否保存代理信息到本地csv文件
        """

        self.__get_proxy_dict = {
            '国内高匿代理HTTP': 'https://www.xicidaili.com/wt/',
            '国内高匿代理HTTPS': 'https://www.xicidaili.com/wn/',
            '西拉免费代理HTTP': 'http://www.xiladaili.com/http/',
            '西拉免费代理HTTPS': 'http://www.xiladaili.com/https/'
            }
        self.__filename = "Proxy_IP.csv"
        self.__is_write_info = writeproxy
        self.__ip_proxy_cn = {}		# 国内高匿代理
        self.__ip_proxy_fr = {}		# 国外高匿代理
        self.__collection = set_mongo()
        self.__re = redis_setting
        self.__re_key = proxy_redis_keys


    def set_redis(self):
        r = redis.Redis(host=self.__re_host, port=self.__re_port, password=self.__re_passwd, db=self.__re_db)
        return r

    def __query_ip(self, url, **kwargs):
        """ 请求IP代理的网址 """
        headers = {}
        params = {}
        data = {}
        name = kwargs['name']
        page = kwargs['page']

        if len(kwargs) > 0:
            headers = kwargs['headers']

            try:
                params = kwargs['params']
            except:
                pass

            try:
                data = kwargs['data']
            except:
                pass
            
            try:
                proxy = kwargs['proxies']
            except:
                pass

        failed_count: int = 1
        while 1:
            print('%s:第%s页, 第%s次爬取' % (name, page, failed_count))
            requests.packages.urllib3.disable_warnings()
            res = requests.get(url, headers=headers, params=params, data=data, proxies = proxy, verify=False)
            if res.status_code == 200:
                result = {'code': res.status_code, 'info': res.text}
                print('%s:第%s页, 第%s次爬取成功。' % (name, page, failed_count))
                return result
            elif res.status_code == 503:
                print('%s:第%s页, 第%s次爬取失败！！！' % (name, page, failed_count))
                if failed_count == 3:
                    self.__re.lpush(self.__re_key, url)
                    return {'code': res.status_code, 'info': '服务器出错'}
                time.sleep(0.2)
                failed_count += 1


    def __write_ip(self, infos):
        """
        把获取到的代理IP信息写入到本地csv文件中。
        :param infos: 代理IP信息
        """
        headers = list(infos[0].keys())
        rows = infos

        with open(self.__filename, 'w', newline='')as f:
            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(rows)
        return

    def get_proxy(self):
        """
        解析请求到的网页内容，包括IP地址，端口号，地理位置，运营商该信息，最后检测时间
        """
        proxy_ip_infos = []

        for e_proxy in self.__get_proxy_dict:
            proxy_ip_info = self.__get_proxy(self.__get_proxy_dict[e_proxy], e_proxy)
            if proxy_ip_info['code'] == 200:
                proxy_ip_infos.extend(proxy_ip_info)
                print('"%s"爬取完成！' % e_proxy)
            else:
                print('请求错误代码：%s，爬取"%s"出错，出错原因：%s。' % (proxy_ip_info['code'], e_proxy, proxy_ip_info['info']))

        ip_proxy_dict = {
            '国内': self.__ip_proxy_cn,
            '国外': self.__ip_proxy_fr
        }

        if self.__is_write_info:        # 是否将信息写入文件
            self.__write_ip(proxy_ip_infos)

        req_url = self.__re.rpop()
        while req_url:

            req_url = self.__re.rpop()
        return ip_proxy_dict


    def __get_proxy(self, ip, name):
        proxy_info = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        res = {}
        for index in range(1, 51):
            query_ip = ip + str(index)
            find_dict = {'type': 'HTTPS'} if ip.startswith('https') else {'type': 'HTTP'}
            get_proxys = list(self.__collection.find(find_dict, {'_id': 0}))
            proxy = {}
            if get_proxys:
                get_proxy = random.choice(get_proxys)
                proxy[get_proxy['type']] = get_proxy['type'] + '://' + get_proxy['ip'] + ':' + get_proxy['port']
            else:
                proxy = {'https': 'https://115.53.17.109:9999'}
            res = self.__query_ip(query_ip, headers=headers, name=name, page=index, proxies=proxy, verify=False)
            if res['code'] == 200:
                et = etree.HTML(res['info'])

                if name == '国内高匿代理':
                    trs = et.xpath('//table[@id="ip_list"]//tr')[1:]
                    for tr in trs:
                        # if float(tr.xpath('td//div[@class="bar"]/@title')[0].split('秒')[0]) < 1.2:
                        tds_text_list = [e_text for e_text in tr.xpath('td//text()') if '\n' not in e_text]
                        if tds_text_list[3] == '高匿':
                            proxy_info = self.__assamble_proxy(tds_text_list, name)

                if name.startswith('西拉免费代理'):
                    trs = et.xpath('//table[@class="fl-table"]//tr')[1:]
                    for tr in trs:
                        tds_text_list = [e_text for e_text in tr.xpath('td//text()') if '\n' not in e_text]
                        # if float(tds_text_list[4]) < 3.5:
                        if tds_text_list[2].startswith('高匿'):
                            proxy_info = self.__assamble_proxy(tds_text_list, name)

        return proxy_info


    def __assamble_proxy(self, tds_text_list, name):
        e_ip_info = {}
        proxy_info = []
        proxy_type = proxy_ip = proxy_port = addr = alive_time = ''
        if name == '国内高匿代理':
            proxy_type = tds_text_list[4]
            proxy_ip = tds_text_list[0]
            proxy_port = tds_text_list[1]
            addr = tds_text_list[2]
            alive_time = tds_text_list[5]  # 生存时间，alive time

        if name.startswith('西拉免费代理'):
            proxy_type = tds_text_list[1][:-2]
            proxy_ip = tds_text_list[0].split(':')[0]
            proxy_port = tds_text_list[0].split(':')[1]
            addr = tds_text_list[3]
            alive_time = tds_text_list[5]  # 生存时间，alive time

        self.__assamble_proxy_ip(proxy_type, proxy_ip, proxy_port,name)
        e_ip_info['IP地址'] = proxy_ip
        e_ip_info['端口'] = proxy_port
        e_ip_info['类型'] = proxy_type
        e_ip_info['服务器地址'] = addr
        e_ip_info['生存时间'] = alive_time
        e_ip_info['是否高匿'] = '高匿'
        proxy_info.append(e_ip_info)
        return proxy_info


    def __assamble_proxy_ip(self, proxy_type, proxy_ip, proxy_port, name):
        proxy_type = str(proxy_type)
        proxy = proxy_ip + ":" + proxy_port

        if name.startswith('西拉免费代理'):
            if len(proxy_type) == 4 or len(proxy_type) > 5:
                proxy_type = 'HTTP'
            
            if len(proxy_type) > 4:
                proxy_type = 'HTTPS'

        #     proxy_ip, proxy_port = self.__test_proxy(proxy_ip, proxy_port)
        #     if proxy_ip:
        #         try:
        #             proxy_info = {'type': proxy_type, 'ip': proxy_ip, 'port': proxy_port}
        #             self.__collection.insert_one(proxy_info)
        #             self.__ip_proxy_cn[proxy_type].append(proxy)
        #         except:
        #             self.__ip_proxy_cn[proxy_type] = []
        #             self.__ip_proxy_cn[proxy_type].append(proxy)
        #
        # else:
        proxy_ip, proxy_port = self.__test_proxy(proxy_ip, proxy_port)
        if proxy_ip:
            try:
                proxy_info = {'type': proxy_type, 'ip': proxy_ip, 'port': proxy_port}
                self.__collection.insert_one(proxy_info)
                self.__ip_proxy_cn[proxy_type].append(proxy)
            except:
                self.__ip_proxy_cn[proxy_type] = []
                self.__ip_proxy_cn[proxy_type].append(proxy)
        return

    def __test_proxy(self, ip, port):
        try:
            telnetlib.Telnet(ip, port, timeout=8)
        except:
            return
        else:
            return ip, port


if __name__ == '__main__':
    print("使用说明： \n\t"
          "1.请确保安装了requests 和 lxml;\n\t"
          "2.把该文件放到需要代理的项目中;\n\t"
          "3.导入类名：from xxx.get_proxy import GetProxy; \n\t"
          "4.实例化对象：proxy = GetProxy();\n\t"
          "5.获取代理信息：proxy_list = proxy.get_proxy()\n\n")

    proxy = GetProxy()

    while 1:
        proxy_info = proxy.get_proxy()


    # try:
    #     [print('\t共爬取%s个"%s:%s"代理，输出信息(该信息每次可能会不同)：\n\t\t%s\n\n' % (len(proxy_info[key1][key2]), key1,
    #         key2, proxy_info[key1][key2])) for key1 in proxy_info.keys() for key2 in proxy_info[key1]]
    # except:
    #     print('未获取到任何代理ip.')

    # print('说明：\n\t'
    #       '如果想生成代理信息文件，则可以在实例化类时，设置：proxy = GetProxy(writeproxy=True)\n\n')
    #       '在使用该设置后，在该文件的 同级目录 下会生成一个文件： "Proxy_IP.csv" , '

    input('按"Enter"退出......')


