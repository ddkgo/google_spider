# -*- coding: utf-8 -*-

import scrapy
import re
from urllib import parse
from scrapy.http import Request
from GoogleSearchSpider.items import GooglesearchspiderItem  # 导入item
from GoogleSearchSpider.Utils.datamanager import DataMananger

class searchSpider(scrapy.Spider):
    name = "googlesearch"
    allowed_domains = ["www.google.com"]
    keyword = None
    start_urls = []

    def __init__(self):
        word = input('请输入搜索关键词...')
        print(word)
        self.keyword = word.strip()
        DataMananger().connect()
        DataMananger().create_table(self.keyword)
        url = 'https://www.google.com/search?q=%s' % parse.quote(self.keyword )
        self.start_urls.append(url)

    def parse(self,response):
        print('解析谷歌搜索返回')
        print(response)
        return self.parseOnePage(response)

    def getMailAddFromFile(self, response):
        regex = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b", re.IGNORECASE)
        mails = re.findall(regex, response.text)
        matchMails = []
        for mail in mails:
            pattern = re.compile(r"/\.[jpg|gif|png]/i");
            match = pattern.findall(mail)
            if match:
                print('是张图片')
            else:
                matchMails.append(mail)

        mails_str = ','.join(matchMails)
        return mails_str

    def parseMail(self, response):
        item = response.meta['item']
        item['mail'] = self.getMailAddFromFile(response)
        print('解析邮箱返回')
        print(item)
        yield item

    def parseOnePage(self,response):
        n = 0
        url_to_follow = response.css(".r>a::attr(href)").extract()
        url_to_follow = [url.replace('/url?q=', '') for url in url_to_follow]
        for url in url_to_follow:
            print('解析页面')
            print(url)
            item = GooglesearchspiderItem()
            item['url'] = url
            item['destext'] = ''
            item['ext'] = ''
            request = Request(url, callback=self.parseMail, dont_filter=True)
            request.meta['item'] = item
            yield request

        next_pages_urls = response.css("#foot table a::attr(href)").extract()
        for page_num, url in enumerate(next_pages_urls):
            if (page_num < 100):
                next_page_url = response.urljoin(url)
                yield scrapy.Request(
                    url=next_page_url, callback=self.parse, dont_filter=True)
            else:
                break