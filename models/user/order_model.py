#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging

class OrderModel():

    @gen.coroutine
    def CheckOrderList(self, uaid, OrderTicket):
        # 返回查询的列表的所有订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "SELECT uaid,etime,sl,tp,orderid FROM trader WHERE uaid=%s AND orderid in %s" % (uaid, OrderTicket)
                    yield cursor.execute(sql)
                    datas = cursor.fetchall()
                    return datas
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[OrderModel:CheckOrderList:SELECT]: %s" % err)
                    logging.error("[OrderModel:CheckOrderList:SELECT]: %s" % sql)
                    return []

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
                    logging.error("[OrderModel:AddOrder:INSERT]: %s" % err)
                    return False

    @gen.coroutine
    def AddOrderList(self, order_Tuple_add):
        # 增加订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO trader(uaid,orderid,proname,num,t_type,stime,sprice,etime,eprice,sl,tp,commission,swap,profit,maxprofit,minprofit,comment,magic,followid) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                # print(order_Tuple_add)
                logging.debug("AddOrderList:%s" % order_Tuple_add)
                try:
                    yield cursor.executemany(sql, order_Tuple_add)
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[OrderModel:AddOrder:INSERT]: %s" % err)
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
                    logging.error("[OrderModel:UpOrder:update]: %s" % err)
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
                    logging.error("[OrderModel:UpOrder:update]: %s" % err)
                    return False

    @gen.coroutine
    def UpOrderFollowID(self, orderid_str, uaid):
        # 修改订单FollowID
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update trader set  followid = tid WHERE uaid=%s AND orderid in (%s)"
                # print(sql % (uaid, orderid_str))
                try:
                    yield cursor.execute(sql, (uaid, orderid_str))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[OrderModel:UpOrderFollowID:update]: %s" % err)
                    return False

    @gen.coroutine
    def get_PositionOrder(self, uaid):
        # 查持有订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT tid,uaid,proname,num,t_type,stime,sprice,sl,tp,followid FROM trader WHERE uaid=%s AND etime<=0 AND t_type<2" % uaid
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                return datas

    @gen.coroutine
    def get_PositionOrderNum(self, uaid):
        # 查持有订单数量
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT count(*) AS pnum FROM trader WHERE uaid=%s AND etime<=0 AND t_type<2" % uaid
                logging.debug(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchone()
                return datas['pnum']

    @gen.coroutine
    def get_PositionOrderNum2(self, followid, uaid):
        # 查指定策略的跟单账号持有此策略的订单数量
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT count(*) AS pnum FROM trader WHERE uaid=%s AND etime<=0 AND t_type<2 AND magic=%s" % (uaid, int("9947" + str(followid)))
                logging.debug(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchone()
                return datas['pnum']

    @gen.coroutine
    def findFollowid(self, strComment, uaid):
        # 根据备注查找订单的跟单ID
        import re
        par = "([0-9]+)"
        arr1 = re.compile(par).findall(strComment)
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT tid,followid FROM trader WHERE uaid=%s AND orderid=%s" % (uaid, int(arr1[0]))
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchone()
                if datas:
                    if datas['followid'] == 0:
                        return datas['tid']
                    else:
                        return datas['followid']
                else:
                    return 0

    @gen.coroutine
    def FormatTuple(self, dic_vol):
        listvol = []
        for i in dic_vol:
            listvol.append(int(i))
        listvol.append(1)
        return tuple(listvol)