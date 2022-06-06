import sys
import pymysql
import logging
from config import MYSQL_INFO

logger = logging.getLogger('Main')
class mysql_open():
    def __init__(self):
        try:
            self.conn = pymysql.connect(host=MYSQL_INFO["host"],
                                   user=MYSQL_INFO["user"],
                                   password=MYSQL_INFO["password"],
                                   db=MYSQL_INFO["db"],
                                   port=MYSQL_INFO["port"],
                                   charset='utf8')
            logger.info("Connect MySql Ok")
        except Exception as err:
            logger.error("Connect MySql Fail %s" % err)
            sys.exit(0)

    def __del__(self):
        self.conn.close()
        logger.info("Close MySql")

    #增加联合唯一性
    def add_unique(self):
        try:
            cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            effect_row2 = cursor.execute("alter table trader add unique key (`uaid`, `orderid`)")
            self.conn.commit()
            print("alterTable Ok")
        except Exception as err:
            self.conn.rollback()
            print("alterTable %s" % err)

if __name__ == "__main__":
    mysql_o = mysql_open()
    mysql_o.add_unique()