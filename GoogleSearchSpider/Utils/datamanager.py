import pymysql
from scrapy.utils.project import get_project_settings

class DataMananger():
    dbpool = None
    keyWord = None

    def __new__(cls):
        # 关键在于这，每一次实例化的时候，我们都只会返回这同一个instance对象
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataMananger, cls).__new__(cls)
        return cls.instance

    def connect(self):
        settings = get_project_settings()
        mysqlList = [settings['MYSQL_HOST'],settings['MYSQL_USER'],settings['MYSQL_PASSWD'],settings['MYSQL_DBNAME']]
        dbpool = pymysql.connect(mysqlList[0],mysqlList[1],mysqlList[2],mysqlList[3])

        self.dbpool = dbpool
        return

    def create_table(self,key):
        self.keyWord = key
        # 使用 execute() 方法执行 SQL，如果表不存在就创建
        cursor = self.dbpool.cursor()

        # 使用预处理语句创建表
        sqlDel = "DROP TABLE IF EXISTS GOOGLE_RESULT_%s;" % key
        # 使用预处理语句创建表
        sqlGoogle = """CREATE TABLE IF NOT EXISTS GOOGLE_RESULT_%s(
                                Id INT PRIMARY KEY AUTO_INCREMENT,
                                url VARCHAR(1000),
                                mail VARCHAR(1000),
                                destext VARCHAR(1000),
                                ext VARCHAR(100),
                                lastStamp DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)""" % key

        cursor.execute(sqlDel)
        cursor.execute(sqlGoogle)
        return

    def insert_item(self,item):
        dbObject = self.dbpool
        cursor = dbObject.cursor()
        sql = "INSERT INTO GOOGLE_RESULT_%(url,mail,destext,ext) VALUES(%s,%s,%s,%s)" % self.keyWord
        try:
            cursor.execute(sql, (
                item['url'], item['mail'], item['destext'], item['ext']))
            cursor.connection.commit()
        except BaseException as e:
            print("错误在这里>>>>>>>>>>>>>", e, "<<<<<<<<<<<<<错误在这里")
            dbObject.rollback()