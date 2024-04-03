#coding=utf-8
from tornado import gen
import pymysql
from handlers.myredis.redis_class import RedisClass
from config import redis_qq_pid
from config import redis_version_pid
from libs.db.mysqlopen import mysql_open
import logging
from models.user.master_model import MasterModel
import config

logger = logging.getLogger('Main')
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
    # text = ""
    for Pdata in datas:
        # print(Pdata)
        R.RH.set(redis_qq_pid + str(Pdata['pid']), Pdata['qq'])
        R.RH.set(redis_version_pid + str(Pdata['pid']), Pdata['version'])
        # text = text + "add Product:" + str(Pdata['pid']) + "\n"
    return

# 获取策略账户资料
def getMaster():
    mysql = mysql_open()
    cursor = mysql.conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "SELECT tid,key_ma,uaid,proname,num,t_type,stime,sprice,sl,tp,fx_comment FROM m_trader WHERE flag_ma=1 and eprice=0"
    cursor.execute(sql)
    datas = cursor.fetchall()
    cursor.close()
    return datas

#写入策略账户资料到Redis
@gen.coroutine
def updataRedisMasterAll():
    # 写入Master账户ID与订单号集合
    R = RedisClass()
    #清除所有旧数据
    yield R.delete_redis(config.redis_order_set)
    yield R.delete_redis(config.redis_order_dic)
    #获取数据
    order_arr = getMaster()
    #写入
    # text = ""
    for order in order_arr:
        R.RH.sadd(config.redis_master_uaid_set, str(order['uaid']))
        R.RH.hset(config.redis_master_uaid_dic, order['key_ma'], str(order['uaid']))
        # R.RH.hset(config.redis_master_uaid_dic, "comment_" + order['key_ma'], str(order['fx_comment']))
        R.insert_master_Comment(order['key_ma'], order['fx_comment'])
        # R.RH.sadd(config.redis_order_set + str(order['uaid']), order['tid'])
        # R.RH.hmset(config.redis_order_dic + str(order['tid']), order)
        # text = text + "add Master:" + str(order['uaid']) + "\n"
        # logger.info("add Master:" + str(order['uaid']))
    return

# 写入跟单账号到策略Redis
@gen.coroutine
def updataMasterCopy():
    R = RedisClass()
    R.RH.set("server_ip", config.Server_IP)
    # R.RH.set("server_ip", "64.31.63.259:9008")
    uaidList = R.RH.smembers(config.redis_master_uaid_set)
    M = MasterModel()
    for uaid in uaidList:
        datas2 = yield M.getMaterFollow(uaid)
        yield R.getRedisMaterFollow(datas2)
        # text = text + " add MasterCopy:" + str(uaid) + "\n"
        # logger.info(" add MasterCopy:" + str(uaid))
    return
@gen.coroutine
def start_fu():
    # 启动服务前，要加载的程序和数据，redis
    # ioloop = tornado.ioloop.IOLoop.instance()
    # setRedisProduct(ioloop.run_sync(getProduct))
    # 产品资料批量写入redis
    # text = ""
    datas = getProduct()
    setRedisProduct(datas)
    yield updataRedisMasterAll()
    yield updataMasterCopy()
    return


