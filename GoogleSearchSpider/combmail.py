from GoogleSearchSpider.Utils.datamanager import DataMananger
import pymysql
from scrapy.utils.project import get_project_settings
import re

class combMailDataManager(object):
    def connect(self):
        settings = get_project_settings()
        mysqlList = [settings['MYSQL_HOST'],settings['MYSQL_USER'],settings['MYSQL_PASSWD'],settings['MYSQL_DBNAME']]
        dbpool = pymysql.connect(mysqlList[0],mysqlList[1],mysqlList[2],mysqlList[3])

        self.dbpool = dbpool
        return

    def create_mailtable(self, key):
        # 使用 execute() 方法执行 SQL，如果表不存在就创建
        cursor = self.dbpool.cursor()

        # 使用预处理语句创建表
        sqlDel = "DROP TABLE IF EXISTS GOOGLE_MAILRESULT_%s;" % key
        # 使用预处理语句创建表
        sqlGoogle = """CREATE TABLE IF NOT EXISTS GOOGLE_MAILRESULT_%s(
                                        Id INT PRIMARY KEY AUTO_INCREMENT,
                                        mail VARCHAR(1000),
                                        lastStamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)""" % key

        cursor.execute(sqlDel)
        cursor.execute(sqlGoogle)
        return

    def insert_mail(self,key):
        dbObject = self.dbpool
        cursor = dbObject.cursor()
        totoalMails = []
        # SQL 查询语句
        sql = "SELECT mail FROM GOOGLE_REQMAILRESULT_%s where mail <> ''"% key

        maildataname = "INSERT INTO GOOGLE_MAILRESULT_%s" % key
        insertsql = maildataname + "(mail) VALUES(%s)"
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            print(results)
            for row in results:
                mails = row[0]
                mailArry = mails.split(',')
                for mail in mailArry:
                    totoalMails.append(mail)

            if len(totoalMails) > 0:
                print("start send email!")
                for mail in totoalMails:
                    print(mail)
                    if self.cheack_email(key,mail):
                        try:
                            cursor.execute(insertsql, (mail))
                            cursor.connection.commit()
                        except BaseException as e:
                            print("错误在这里>>>>>>>>>>>>>", e, "<<<<<<<<<<<<<错误在这里")
                            dbObject.rollback()

        except:
            print("Error: unable to fetch data")

    def cheack_email(self, key, mail):
        pattern = re.compile(r"/*.(jpg|gif|png)")
        match = pattern.findall(mail)
        if match:
            print('是张图片')
            return False

        dbObject = self.dbpool
        cursor = dbObject.cursor()

        # SQL 查询语句
        sql = "SELECT * FROM GOOGLE_MAILRESULT_%s where mail='%s'" % (key, mail)
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            if len(results)>0:
                print("%s,邮件已存在，不重复收录" % mail)
                return False
            else:
                return True
        except:
            print("Error: unable to fetch data")

        return False

if __name__ == '__main__':
    word = get_project_settings()["SEARCH_WORDKEY"]
    keyword = word.replace(' ', '')
    a = combMailDataManager()
    a.connect()
    a.create_mailtable(keyword)
    a.insert_mail(keyword)