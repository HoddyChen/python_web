#coding=utf-8
import tormysql
import pymysql
from config import MYSQL_INFO

pool = tormysql.ConnectionPool(
    max_connections=20,  # max open connections
    idle_seconds=7200,  # conntion idle timeout time, 0 is not timeout
    wait_connection_timeout=3,  # wait connection timeout
    host=MYSQL_INFO["host"],
    user=MYSQL_INFO["user"],
    passwd=MYSQL_INFO["password"],
    db=MYSQL_INFO["db"],
    charset="utf8",
    port=MYSQL_INFO["port"],
    autocommit=True,
    cursorclass=pymysql.cursors.DictCursor
)
def fx_escape_string(str_text):
    return pymysql.escape_string(str_text)
# from tornado.ioloop import IOLoop
# from tornado import gen
# @gen.coroutine
# def test():
#     with (yield pool.Connection()) as conn:
#         try:
#             with conn.cursor() as cursor:
#                 yield cursor.execute("INSERT INTO test(id) VALUES(1)")
#         except:
#             yield conn.rollback()
#         else:
#             yield conn.commit()
#
#         with conn.cursor() as cursor:
#             yield cursor.execute("SELECT * FROM test")
#             datas = cursor.fetchall()
#
#     printdatas
#
#     yield pool.close()
#
#
# ioloop = IOLoop.instance()
# ioloop.run_sync(test)



