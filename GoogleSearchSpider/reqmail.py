from GoogleSearchSpider.Utils.datamanager import DataMananger
import pymysql
from scrapy.utils.project import get_project_settings
import requests
import re

class reqMailDataManager(object):
    keyWord = None;
    dbpool = None;

    def connect(self):
        settings = get_project_settings()
        mysqlList = [settings['MYSQL_HOST'],settings['MYSQL_USER'],settings['MYSQL_PASSWD'],settings['MYSQL_DBNAME']]
        dbpool = pymysql.connect(mysqlList[0],mysqlList[1],mysqlList[2],mysqlList[3])

        self.dbpool = dbpool
        return

    def create_reqmailtable(self, key):
        self.keyWord = key
        # 使用 execute() 方法执行 SQL，如果表不存在就创建
        cursor = self.dbpool.cursor()
        # 使用预处理语句创建表
        sqlDel = "DROP TABLE IF EXISTS GOOGLE_REQMAILRESULT_%s;" % key
        # 使用预处理语句创建表
        sqlGoogle = """CREATE TABLE IF NOT EXISTS GOOGLE_REQMAILRESULT_%s(
                                       Id INT PRIMARY KEY AUTO_INCREMENT,
                                       url VARCHAR(1000),
                                       mail VARCHAR(1000),
                                       destext VARCHAR(1000),
                                       ext VARCHAR(100),
                                       lastStamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)""" % key

        cursor.execute(sqlDel)
        cursor.execute(sqlGoogle)
        return

    def req_mail(self,key):
        dbObject = self.dbpool
        cursor = dbObject.cursor()
        # SQL 查询语句
        sql = "SELECT * FROM GOOGLE_RESULT_%s"% self.keyWord
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            for row in results:
                item = {}
                item['url'] = row[1]
                item['mail'] = row[2]
                item['destext'] = row[3]
                item['ext'] = row[4]
                try:
                    response = requests.get(item['url'], timeout=10)
                    if response.status_code == 200:
                        item['mail'] = self.getMailAddFromFile(response)
                        print('解析邮箱返回')
                        print(item)
                        self.insert_item(item)
                except:
                    print('fail %s' % item['url'])

        except:
            print("Error: unable to fetch data")


    def getMailAddFromFile(self, response):
        regex = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b", re.IGNORECASE)
        mails = re.findall(regex, response.text)
        matchMails = []
        for mail in mails:
                matchMails.append(mail)

        mails_str = ','.join(matchMails)
        return mails_str

    def insert_item(self,item):
        dbObject = self.dbpool
        cursor = dbObject.cursor()
        dataname = "INSERT INTO GOOGLE_REQMAILRESULT_%s" % self.keyWord
        sql = dataname+"(url,mail,destext,ext) VALUES(%s,%s,%s,%s)"
        try:
            cursor.execute(sql, (
                item['url'], item['mail'], item['destext'], item['ext']))
            cursor.connection.commit()
        except BaseException as e:
            print("错误在这里>>>>>>>>>>>>>", e, "<<<<<<<<<<<<<错误在这里")
            dbObject.rollback()

if __name__ == '__main__':
    word = get_project_settings()["SEARCH_WORDKEY"]
    keyword = word.replace(' ', '')
    a = reqMailDataManager()
    a.connect()
    a.create_reqmailtable(keyword)
    a.req_mail(word)

