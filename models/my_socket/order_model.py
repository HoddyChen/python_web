#coding=utf-8
from tornado import gen
import logging
import re
from handlers.myredis.redis_class import RedisClass
import pymysql
from libs.db.dbsession import pool
from libs.db.mysqlopen import mysql_open

logger = logging.getLogger('Socket')
class OrderModel():
    # logger = logging.getLogger('Main')

    @gen.coroutine
    def CheckOrderList(self, uaid, OrderTicket):
        # 返回查询的列表的所有订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "SELECT uaid,t_type,etime,sl,tp,orderid,num FROM trader WHERE uaid=%s AND orderid in %s" % (uaid, OrderTicket)
                    yield cursor.execute(sql)
                    datas = cursor.fetchall()
                    if datas != None:
                        return datas
                    else:
                        return None
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[OrderModel:CheckOrderList:SELECT]: %s" % err)
                    logger.error("[OrderModel:CheckOrderList:SELECT]: %s" % sql)
                    return False

    def CheckOrder(self, uaid, orderid, CloseT, OrderStopLoss, OrderTakeProfit):
        # 查订单存在与否
        edit_flag = 0
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT uaid,etime,sl,tp FROM trader WHERE uaid=%s AND orderid=%s" % (uaid, orderid)
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchone()
                if datas != None:
                    if CloseT != datas['etime']:
                        edit_flag = 1
                    if OrderStopLoss != datas['sl']:
                        edit_flag = 1
                    if OrderTakeProfit != datas['tp']:
                        edit_flag = 1
                else:
                    return None
                if edit_flag == 0:
                    return True
                else:
                    return False

    @gen.coroutine
    def AddOrder(self, uaid, orderid, proname, num, t_type, stime, sprice, etime, eprice, sl, tp, commission, swap, profit, maxprofit, minprofit, comment, magic, followid):
        # 增加订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO trader(uaid,orderid,proname,num,t_type,stime,sprice,etime,eprice,sl,tp,commission,swap,profit,maxprofit,minprofit,comment,magic,followid) VALUES(%s,%s,'%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s',%s,%s)"
                try:# print(sql)
                    yield cursor.execute(sql % (uaid, orderid, proname, num, t_type, stime, sprice, etime, eprice, sl, tp, commission, swap, profit, maxprofit, minprofit, comment, magic, followid))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[OrderModel:AddOrder:INSERT]: %s" % err)
                    return False

    @gen.coroutine
    def AddOrderList(self, order_Tuple_add):
        # 增加订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO trader(uaid,orderid,proname,num,t_type,stime,sprice,etime,eprice,sl,tp,commission,swap,profit,maxprofit,minprofit,comment,magic,followid) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                # print(order_Tuple_add)
                # self.logger.info(order_Tuple_add)
                try:
                    yield cursor.executemany(sql, order_Tuple_add)
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[OrderModel:AddOrder:INSERT]: %s" % err)
                    return False

    @gen.coroutine
    def UpOrder(self, uaid, orderid, proname, num, t_type, stime, sprice, etime, eprice, sl, tp, commission, swap, profit, maxprofit, minprofit, comment, magic, followid):
        # 修改订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update trader set proname='%s',num=%s,t_type=%s,stime=%s,sprice=%s,etime=%s,eprice=%s,sl=%s,tp=%s,commission=%s,swap=%s,profit=%s,maxprofit=%s,minprofit=%s,comment='%s',magic=%s WHERE uaid=%s AND orderid=%s"
                try:# print(sql)
                    yield cursor.execute(sql % (proname, num, t_type, stime, sprice, etime, eprice, sl, tp, commission, swap, profit, maxprofit, minprofit, comment, magic, uaid, orderid))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[OrderModel:UpOrder:update]: %s" % err)
                    return False

    @gen.coroutine
    def UpOrderList(self, order_Tuple_edit):
        # 修改订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update trader set proname=%s,num=%s,t_type=%s,stime=%s,sprice=%s,etime=%s,eprice=%s,sl=%s,tp=%s,commission=%s,swap=%s,profit=%s,maxprofit=%s,minprofit=%s,comment=%s,magic=%s WHERE uaid=%s AND orderid=%s"
                try:# print(sql)
                    yield cursor.executemany(sql, order_Tuple_edit)
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[OrderModel:UpOrder:update]: %s" % err)
                    return False

    @gen.coroutine
    def UpOrderFollowID(self, orderid_new_list, uaid):
        # 修改订单FollowID
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update trader set  followid = tid WHERE uaid=%s AND orderid in %s"
                # print(sql % (uaid, orderid_str))
                try:
                    yield cursor.execute(sql, (uaid, orderid_new_list))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[OrderModel:UpOrderFollowID:update]: %s" % err)
                    return False

    @gen.coroutine
    def get_PositionOrder2(self, uaid):
        # 查持有订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT SQL_NO_CACHE tid,uaid,proname,num,t_type,stime,sprice,sl,tp,followid FROM trader WHERE uaid=%s AND etime<=0 AND t_type<2" % uaid
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                return datas

    @gen.coroutine
    def get_PositionOrder(self, uaid):
        # 查持有订单
        try:
            Mysql = mysql_open()
            cursor = Mysql.conn.cursor(cursor=pymysql.cursors.SSDictCursor)
            sql = "SELECT tid,uaid,proname,num,t_type,stime,sprice,sl,tp,followid FROM trader WHERE uaid=%s AND etime<=0 AND t_type<6" % uaid
            cursor.execute(sql)
            datas = []
            for h in cursor:
                # print("pp:%s" % h)
                datas.append(h)
            return datas
        except Exception as err:
            logger.error("[OrderModel:get_PositionOrder]: %s" % err)

    @gen.coroutine
    def findFollowid(self, strComment, uaid):
        # 根据备注查找订单的跟单ID
        par = "([0-9]+)"
        arr1 = re.compile(par).findall(strComment)
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT tid,followid FROM trader WHERE uaid=%s AND orderid=%s" % (uaid, int(arr1[0]))
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchone()
                if datas != None:
                    if datas['followid'] == 0:
                        return datas['tid']
                    else:
                        return datas['followid']
                else:
                    return None


    @gen.coroutine
    def FormatTuple(self, dic_vol):
        listvol = []
        for i in dic_vol:
            listvol.append(int(i['H1']))
        listvol.append(1)
        return tuple(listvol)