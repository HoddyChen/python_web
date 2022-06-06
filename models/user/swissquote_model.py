#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import datetime
import time
import hashlib
import config
from handlers.myredis.redis_class import RedisClass
from models.user.order_model import OrderModel
from models.user.master_model import MasterModel

logger = logging.getLogger('Main')
class SwissquoteModel():
    def __init__(self):
        self.R = RedisClass()

    @gen.coroutine
    def CheckMailAccount(self, umail):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT uid,email FROM users WHERE email=%s and emailflag=1"
                # print(sql)
                yield cursor.execute(sql, umail)
                datas = cursor.fetchone()
        return datas

    @gen.coroutine
    def AddMailAccount(self, umail):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT uid,email FROM users WHERE email=%s and emailflag=1"
                try:
                    up_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql3 = "INSERT INTO users(email,emailflag,vipid,starttime,flag) VALUES('%s', %s, %s, '%s', %s)"
                    yield cursor.execute(sql3 % (umail, 1, 1, up_date, 1))
                    uid = conn.insert_id()
                    # logger.info(sql2)
                    yield conn.commit()
                    return uid
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[SwissquoteModel:AddMailAccount:INSERT]: %s" % err)
                    return None

    @gen.coroutine
    def ExitAccount(self, users):
        if self.R.RH.hexists(config.redis_acount_md5_dic, users['ukid']):
            uaid = self.R.RH.hget(config.redis_acount_md5_dic, users['ukid'])
            self.updataAccount(users, uaid)
            self.R.RH.hdel(config.redis_acount_md5_dic, users['ukid'])
            self.R.RH.delete(config.redis_ua_pid_endtime + str(uaid))
            return "1,1,"
        else:
            # 账户未登陆或已经失效
            return "-13,0,0,0,0,0,"

    @gen.coroutine
    def updataAccount(self, users, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('updata_follow_parameter',
                                          (users['uid'], users['ip'], int(uaid), int(users['maxtime']), int(users['maxloss']), int(users['maxnum']),
                                           float(users['fixed']), float(users['percent']), float(users['rate_min']),
                                           float(users['rate_max']), int(users['reflex']), float(users['rate']),
                                           int(users['allowed_sign']), int(users['parameter_time']), users['MasterKey'], int(users['pid']),
                                           float(users['balance']), float(users['credit']), float(users['quity']),
                                           float(users['profit']), float(users['margin']), "@maxtime", "@maxloss",
                                           "@maxnum", "@fixed", "@percent", "@rate_min", "@rate_max", "@reflex",
                                           "@rate", "@allowed_sign", "@parameter_time", "@flag"))
                    yield cursor.execute("SELECT @maxtime,@maxloss,@maxnum,@fixed,@percent,@rate_min,@rate_max,@reflex,@rate,@allowed_sign,@parameter_time,@flag")
                    row = cursor.fetchone()
                    # print("AA:", row)
                except Exception as err:
                    row = None
                    logger.error("[user_model:updataAccount:update]: %s" % err)
        return row


