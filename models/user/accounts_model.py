#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import config
import datetime
import time
import hashlib
from handlers.myredis.redis_class import RedisClass


class AccountsModel():
    logger = logging.getLogger('Main')

    @gen.coroutine
    def getProductInfoList(self, pid):
        # 返回查询产品价格列表
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "SELECT pid, info1, info2, info3, piid, piname FROM product_info WHERE pid=%s" % (pid,)
                    yield cursor.execute(sql)
                    datas = cursor.fetchall()
                    self.logger.debug(datas)
                    return datas
                except Exception as err:
                    self.logger.error("[AccountsModel:getProductInfoList:SELECT]: %s" % err)
                    self.logger.error("[AccountsModel:getProductInfoList:SELECT]: %s" % sql)
                    return []

    @gen.coroutine
    def getProductInfo(self, piid):
        # 返回查询产品价格详情
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "SELECT pid, info1, info2, info3, piid, piname FROM product_info WHERE piid=%s" % (piid,)
                    yield cursor.execute(sql)
                    datas = cursor.fetchone()
                    # print(datas)
                    return datas
                except Exception as err:
                    self.logger.error("[AccountsModel:getProductInfo:SELECT]: %s" % err)
                    self.logger.error("[AccountsModel:getProductInfo:SELECT]: %s" % sql)
                    return None

    @gen.coroutine
    def getCNY(self):
        # 返回查询人民币价格
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "SELECT big_data_history62.`close` FROM big_data_history62 WHERE big_data_history62.dtime ORDER BY big_data_history62.dtime DESC LIMIT 1"
                    yield cursor.execute(sql)
                    datas = cursor.fetchone()
                    self.logger.debug(datas)
                    return datas
                except Exception as err:
                    self.logger.error("[AccountsModel:getCNY]: %s" % err)
                    self.logger.error("[AccountsModel:getCNY]: %s" % sql)
                    return None

    @gen.coroutine
    def setOrderTwo(self, Odata, uid, pid, followid):
        # 提交支付订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    from models.public.headers_model import Headers_Models
                    H = Headers_Models()
                    # 生成个订单号
                    OrderNo = H.getOrderNo()
                    yield cursor.callproc('setOrderTwo', (followid, uid, pid, Odata['piid'], Odata['PaymentTypes'], Odata['cnh'],
                                                          Odata['fx_num'], Odata['daytype'], Odata['datetype'], OrderNo,"@out_mflag"))
                    yield cursor.execute("select @out_mflag;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    if row != None:
                        return row['@out_mflag'], OrderNo
                    else:
                        return -6
                except Exception as err:
                    self.logger.error("[AccountsModel:setOrderTwo:]: %s" % err)
                    return -6

    # 得到购买订单列表
    @gen.coroutine
    def getAccountsOrderList(self, followid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                if page_main == None or page_main.get('fx_id') == 9:
                    sql = " FROM p_order INNER JOIN product_info ON p_order.piid = product_info.piid WHERE p_order.uaid = %s AND p_order.pid=%s" % (followid, config.PID)
                else:
                    # search = "%" + page_main.get('search') + "%"
                    sql = " FROM p_order INNER JOIN product_info ON p_order.piid = product_info.piid WHERE p_order.uaid = %s AND p_order.pid=%s AND otype = %s" % (followid, config.PID, page_main.get('fx_id'))
                sql2 = "SELECT product_info.piname " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT product_info.piname,product_info.info2,product_info.info3,p_order.onum,p_order.otime," \
                       "p_order.amount_cny,p_order.amount,p_order.otype,product_info.info1,p_order.strattime," \
                       "p_order.endtime,p_order.order_no,p_order.date_num,p_order.payment_type,p_order.potype "\
                       + sql + " ORDER BY p_order.oid DESC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                # print(datas)
                    return datas
                else:
                    return []

    @gen.coroutine
    def send_pay_email(self, pay_str, fx_no):
        from models.user.sendmail_model import SendmailModel
        S = SendmailModel()
        # mail_key = str(random.randint(100000, 999999))

        mail_text = """支付提示：
                        """
        mail_text = mail_text + pay_str + """
                        -----[跟单系统]"""
        tomail = []
        tomail.append("99051131@qq.com")
        send_flag = yield S.email_send(tomail, mail_text, "系统订单支付提示" + str(fx_no))
        return send_flag