# *-* coding:utf-8 *-*
import requests
from bs4 import BeautifulSoup
import lxml
from multiprocessing import Process, Queue
import random
import json
import time
import requests
import re


class ProxiesAbroad_pre(object):
    """docstring for Proxies"""

    def __init__(self,data):
        self.data = data
        self.proxies = []
        self.verify_pro = []

    def get_proxies(self):
        for odd in self.data:
            self.proxies.append("https://"+odd)

    def verify_proxies(self):
        # 没验证的代理
        old_queue = Queue()
        # 验证后的代理
        new_queue = Queue()
        print('verify proxy........')
        works = []
        for _ in range(15):
            works.append(Process(target=self.verify_one_proxy, args=(old_queue, new_queue)))
        for work in works:
            work.start()
        for proxy in self.proxies:
            old_queue.put(proxy)
        for work in works:
            old_queue.put(0)
        for work in works:
            work.join()
        self.proxies = []
        while 1:
            try:
                self.proxies.append(new_queue.get(timeout=1))
            except:
                break
        print('verify_proxies done!')

    def verify_one_proxy(self, old_queue, new_queue):
        while 1:
            proxy = old_queue.get()
            if proxy == 0: break
            protocol = 'https' if 'https' in proxy else 'http'
            proxies = {protocol: proxy}
            try:
                request = requests.get('http://www.google.com/search?q=cycling%20shorts', proxies=proxies, timeout=2)
                if request.status_code == 200:
                    print('success %s' % proxy)
                    new_queue.put(proxy)
                else:
                    print(request.status_code)

            except:
                print('fail %s' % proxy)


if __name__ == '__main__':
    data = []
    for line in open("preip.txt", "r"):  # 设置文件对象并读取每一行文件
        data.append(line)  # 将每一行文件加入到list中

    a = ProxiesAbroad_pre(data)
    a.get_proxies()
    a.verify_proxies()
    print(a.proxies)
    proxie = a.proxies
    with open('proxies.txt', 'a') as f:
        for proxy in proxie:
            f.write(proxy + '\n')