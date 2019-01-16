# -*- coding: utf-8 -*-

import scrapy
import re
import time
from urllib import parse
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from GoogleSearchSpider.items import GooglesearchspiderItem  # 导入item
from GoogleSearchSpider.Utils.datamanager import DataMananger

class searchSpider(scrapy.Spider):
    name = "googlesearch_simple"
    allowed_domains = ["www.google.com"]
    keyword = None
    pageIndex = 0
    start_urls = []

    def __init__(self):
        # word = input('请输入搜索关键词...')
        self.pageIndex = 0
        word = get_project_settings()["SEARCH_WORDKEY"]
        print(word)
        self.keyword = word.strip()
        DataMananger().connect()
        DataMananger().create_table(self.keyword)
        url = 'http://www.google.com/search?q=%s' % parse.quote(self.keyword)
        self.start_urls.append(url)

    def parse(self,response):
        print('解析谷歌搜索返回')
        pageIndex = response.css('#foot table td[class="cur"]::text').extract()
        print('当前界面序号:'+pageIndex[0])
        print(response)
        return self.parseOnePage(response)

    def getMailAddFromFile(self, response):
        regex = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b", re.IGNORECASE)
        mails = re.findall(regex, response.text)
        matchMails = []
        for mail in mails:
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
            if url.find('search?q') == -1:
                print('解析页面')
                print(url)
                item = GooglesearchspiderItem()
                item['url'] = url
                item['destext'] = ''
                item['ext'] = ''
                item['mail'] = ''
                # request = Request(url, callback=self.parseMail, dont_filter=True)
                # request.meta['item'] = item
                yield item

        time.sleep(30)
        next_pages_urls = response.css('#foot table a[id="pnnext"]::attr(href)').extract()
        url = next_pages_urls[0]
        self.pageIndex += 1
        next_page_url = response.urljoin(url)
        if (self.pageIndex < 500):
            yield scrapy.Request(
                url=next_page_url, callback=self.parse, dont_filter=True)
