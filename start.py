#coding=utf-8
import pymysql
from handlers.myredis.redis_class import RedisClass
from config import redis_qq_pid
from config import redis_version_pid
from libs.db.mysqlopen import mysql_open
# import handlers.log.mylog as my_log
from models.user.master_model import MasterModel
import config

# logger = my_log.logInit()
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

# 获取策略账户资料
def getMaster():
    mysql = mysql_open()
    cursor = mysql.conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "SELECT tid,key_ma,uaid,proname,num,t_type,stime,sprice,sl,tp FROM m_trader WHERE flag_ma=1 and eprice=0"
    cursor.execute(sql)
    datas = cursor.fetchall()
    cursor.close()
    return datas

#写入策略账户资料到Redis
def updataRedisMasterAll():
    # 写入Master账户ID与订单号集合
    R = RedisClass()
    #清除所有旧数据
    yield R.delete_redis(config.redis_order_set)
    yield R.delete_redis(config.redis_order_dic)
    #获取数据
    order_arr = getMaster()
    #写入
    for order in order_arr:
        R.RH.sadd(config.redis_master_uaid_set, str(order['uaid']))
        R.RH.hset(config.redis_master_uaid_dic, order['key_ma'], str(order['uaid']))
        R.RH.sadd(config.redis_order_set + str(order['uaid']), order['tid'])
        R.RH.hmset(config.redis_order_dic + str(order['tid']), order)
    return

# 写入跟单账号到策略Redis
def updataMasterCopy():
    R = RedisClass()
    uaidList = R.RH.smembers(config.redis_master_uaid_set)
    M = MasterModel()
    for uaid in uaidList:
        datas2 = yield M.getMaterFollow(uaid)
        yield R.getRedisMaterFollow(datas2)
    return

def start_fu():
    # 启动服务前，要加载的程序和数据，redis
    # ioloop = tornado.ioloop.IOLoop.instance()
    # setRedisProduct(ioloop.run_sync(getProduct))
    # 产品资料批量写入redis
    datas = getProduct()
    setRedisProduct(datas)
    updataRedisMasterAll()
    updataMasterCopy()

