#coding=utf-8
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.escape
import pymysql
from tornado.options import define, options
from handlers.main.main_urls import handlers
from config import settings
from handlers.myredis.redis_class import RedisClass
#定义一个默认的端口
define("port", default=8002, help="run port ", type=int)
# define("t",  default=False, help="creat tables", type=bool)
from libs.db.dbsession import pool
from config import redis_qq_pid
from config import redis_version_pid
from libs.db.mysqlopen import mysql_open

# 获取产品资料
def getProduct():
    mysql = mysql_open()
    cursor = mysql.conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "SELECT pid,qq,version FROM product"
    cursor.execute(sql)
    datas = cursor.fetchall()
    cursor.close()
    return datas

# 产品资料批量写入redis
def setRedisProduct(datas):
    R = RedisClass()
    # print(datas)
    for Pdata in datas:
        # print(Pdata)
        R.RH.set(redis_qq_pid + str(Pdata['pid']), Pdata['qq'])
        R.RH.set(redis_version_pid + str(Pdata['pid']), Pdata['version'])

if __name__ == "__main__":
    # 启动服务前，要加载的程序和数据，redis
    # ioloop = tornado.ioloop.IOLoop.instance()
    # setRedisProduct(ioloop.run_sync(getProduct))
    # 产品资料批量写入redis
    datas = getProduct()
    setRedisProduct(datas)
    R = RedisClass()
    # 写入Master账户ID与订单号集合
    account=[]
    order=[]
    for aid in account:
        str_account = "account" + str(aid)
        for ovol in order:
            R.RH.sadd(str_account, ovol['oid'])
            R.RH.hmset("order" + ovol['oid'], ovol)
    # 启动http服务
    options.parse_command_line()
    app = tornado.web.Application(handlers, **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print('start server...')
    tornado.ioloop.IOLoop.instance().start()

    # server = HTTPServer(application)
    # server.bind(8888)
    # server.start(4)  # Forks multiple sub-processes
    # tornado.ioloop.IOLoop.current().start()