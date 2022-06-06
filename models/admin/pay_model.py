# coding = utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import hashlib
import datetime
import config
from handlers.myredis.redis_class import RedisClass
import json

logger = logging.getLogger('Main')
class PayModel():

    # 得到购买订单列表
    @gen.coroutine
    def getPayOrderList(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                if page_main == None or page_main.get('fx_id') == 9:
                    sql = " FROM p_order INNER JOIN product_info ON p_order.piid = product_info.piid INNER JOIN users ON p_order.uid = users.uid INNER JOIN users_account ON p_order.uaid = users_account.uaid WHERE p_order.pid=%s" % (config.PID,)
                else:
                    # search = "%" + page_main.get('search') + "%"
                    sql = " FROM p_order INNER JOIN product_info ON p_order.piid = product_info.piid INNER JOIN users ON p_order.uid = users.uid INNER JOIN users_account ON p_order.uaid = users_account.uaid WHERE p_order.pid=%s AND otype = %s" % (config.PID, page_main.get('fx_id'))
                if page_main != None and page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    if sql == "":
                        sql = " WHERE p_order.order_no like '%s' OR users.email  like '%s' OR users_account.account like '%s' " % (search, search, search)
                    else:
                        sql = sql + " AND p_order.order_no like '%s' OR users.email  like '%s' OR users_account.account like '%s' " % (search, search, search)

                sql2 = "SELECT product_info.piname " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT product_info.piname,product_info.info2,product_info.info3,p_order.onum,p_order.otime," \
                       "p_order.amount_cny,p_order.amount,p_order.otype,product_info.info1,p_order.strattime," \
                       "p_order.endtime,p_order.order_no,p_order.date_num,p_order.payment_type,p_order.potype," \
                       "p_order.oid,users.email,users_account.account "\
                       + sql + " ORDER BY p_order.oid DESC limit %s, %s" % (int(start), int(length))
                print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                # print(datas)
                    return datas
                else:
                    return []

    @gen.coroutine
    def setPayOrder(self, oid, otype):
        # 提交支付订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('set_pay_type', (oid, otype, "@out_mflag", "@email"))
                    yield cursor.execute("select @out_mflag,@email;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    if row != None:
                        return row['@out_mflag'], row['@email']
                    else:
                        return -6
                except Exception as err:
                    self.logger.error("[PayModel:setPayOrder:]: %s" % err)
                    return -6