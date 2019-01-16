# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from GoogleSearchSpider.Utils.datamanager import DataMananger

class GooglesearchspiderPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        mysqlList = [settings['MYSQL_HOST'],settings['MYSQL_USER'],settings['MYSQL_PASSWD'],settings['MYSQL_DBNAME']]
        dbpool = pymysql.connect(mysqlList[0],mysqlList[1],mysqlList[2],mysqlList[3])
        # 使用 execute() 方法执行 SQL，如果表不存在就创建
        cursor = dbpool.cursor()

        # 使用预处理语句创建表
        sqlDel = "DROP TABLE IF EXISTS GOOGLE_RESULT;"
        # 使用预处理语句创建表
        sqlGoogle = """CREATE TABLE IF NOT EXISTS GOOGLE_RESULT(
                        Id INT PRIMARY KEY AUTO_INCREMENT,
                        url VARCHAR(1000),
                        mail VARCHAR(1000),
                        destext VARCHAR(1000),
                        ext VARCHAR(100),
                        lastStamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)"""

        cursor.execute(sqlDel)
        cursor.execute(sqlGoogle)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        print(item)
        if spider.name == 'googlesearch':
            DataMananger().insert_item(item)
        elif spider.name == 'googlesearch_simple':
            DataMananger().insert_item(item)

        return item

