# -*- coding: utf-8 -*-
# ==================================================
# 对 Timer 做以下再封装的目的是：当某个功能需要每隔一段时间被
# 执行一次的时候，不需要在回调函数里对 Timer 做重新安装启动
# ==================================================
__author__ = 'liujiaxing'

from threading import Timer
from datetime import datetime

import get_proxy as gp
from settings import proxy_spider_delta_time


class MyTimer(object):

    def __init__(self, start_time, interval, callback_proc, args=None, kwargs=None):
        self.__timer = None
        self.__start_time = start_time
        self.__interval = interval
        self.__callback_pro = callback_proc
        self.__args = args if args is not None else []
        self.__kwargs = kwargs if kwargs is not None else {}

    def exec_callback(self, args=None, kwargs=None):
        self.__callback_pro(*self.__args, **self.__kwargs)
        self.__timer = Timer(self.__interval, self.exec_callback)
        self.__timer.start()

    def start(self):
        interval = self.__interval - (datetime.now().timestamp() - self.__start_time.timestamp())
        print(interval)
        self.__timer = Timer(interval, self.exec_callback)
        self.__timer.start()

    def cancel(self):
        self.__timer.cancel()
        self.__timer = None


if __name__ == "__main__":
    aa = gp.GetProxy()
    func = aa.get_proxy()
    start = datetime.now().replace(minute=3, second=0, microsecond=0)
    tmr = MyTimer(start, proxy_spider_delta_time * 60, func)
    tmr.start()
    tmr.cancel()