#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import config
import datetime
import time
import hashlib
from handlers.myredis.redis_class import RedisClass


class SeperateModel():
    logger = logging.getLogger('Main')

    @gen.coroutine
    def delSeperateList(self, fid):
        # 删除表中的相关的所有订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "DELETE FROM seperate_arr WHERE fid=%s" % (fid,)
                    yi = yield cursor.execute(sql)
                    datas = cursor.fetchall()
                    # print("delSeperateList:yi:", yi)
                    # print("delSeperateList:", datas)
                    return datas
                except Exception as err:
                    yield conn.rollback()
                    self.logger.error("[SeperateModel:delSeperateList:SELECT]: %s" % err)
                    self.logger.error("[SeperateModel:delSeperateList:SELECT]: %s" % sql)
                    return []

    @gen.coroutine
    def CheckFollowID(self, uaid, followid):
        # 查跟单表的ID
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT fid FROM follow WHERE uaid=%s AND followid=%s" % (uaid, followid)
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchone()
                if datas != None:
                    return datas['fid']
                else:
                    return 0

    @gen.coroutine
    def AddSeperateList(self, order_Tuple_add):
        # 增加订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO seperate_arr(fid,orderid,qsid) VALUES(%s,%s,%s)"
                # print(order_Tuple_add)
                self.logger.info(order_Tuple_add)
                try:
                    yield cursor.executemany(sql, order_Tuple_add)
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    self.logger.error("[SeperateModel:AddSeperateList:INSERT]: %s" % err)
                    return False

    @gen.coroutine
    def getSeperateOrder(self, fid):
        # 查所有
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT orderid,qsid FROM seperate_arr WHERE fid=%s" % fid
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                return datas

    @gen.coroutine
    def FormatTuple(self, dic_vol):
        listvol = []
        for i in dic_vol:
            listvol.append(int(i))
        listvol.append(1)
        return tuple(listvol)