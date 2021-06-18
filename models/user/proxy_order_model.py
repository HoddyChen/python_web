#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging

class ProxyOrderModel():

    @gen.coroutine
    def CheckOrderList(self, uaid, OrderTicket):
        # 返回查询的列表的所有订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "SELECT * FROM proxy_order WHERE uaid=%s AND orderid in %s" % (uaid, OrderTicket)
                    yield cursor.execute(sql)
                    datas = cursor.fetchall()
                    return datas
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:CheckOrderList:SELECT]: %s" % err)
                    logging.error("[ProxyOrderModel:CheckOrderList:SELECT]: %s" % sql)
                    return []

    @gen.coroutine
    def CheckProxyOrder(self, account):
        # 查代理账号的返佣是不是存在
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT account FROM proxy_order WHERE account=%s limit 0,1" % (account,)
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    return True
                else:
                    return False

    @gen.coroutine
    def editPAVerify2(self, account):
        # 更改账号的返佣状态
        p_flag = yield self.CheckProxyOrder(account)
        if p_flag == True:
            verify_flag = 2
        else:
            verify_flag = 1
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update proxy_account set verify=%s WHERE account=%s"
                try:
                    yield cursor.execute(sql % (verify_flag, account))
                    yield conn.commit()
                    if p_flag == True:
                        return 5
                    else:
                        return 1

                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:editPAVerify:update]: %s" % err)
                    return -1


    @gen.coroutine
    def editPAVerify3(self):
        # 初始化未激活的返佣状态
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update proxy_account set verify=0 WHERE verify=1"
                try:
                    num = yield cursor.execute(sql)
                    yield conn.commit()
                    return num
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:editPAVerify3:update]: %s" % err)
                    return 0


    # 修改佣金状态，接受返佣
    @gen.coroutine
    def editPAVerify(self, uid, account, PROXY_PRICE):
        the_stime, the_etime = yield self.getStime('the_week')
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('edit_proxy_verify', (uid, PROXY_PRICE, account, the_stime, "@out_mflag"))
                    yield cursor.execute("select @out_mflag;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    return row['@out_mflag']
                except Exception as err:
                    logging.error("[ProxyOrderModel:editPAVerify:update]: %s" % err)
                    return -1

    @gen.coroutine
    def CheckUserAccount(self, account, a_code):
        # 查账号存在与否
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT allname, soft_id FROM users_account WHERE pt_id=20 AND account=%s" % (account,)
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchone()
                if datas != None:
                    datas['allname'] = datas['allname'].strip()
                    datas['allname'] = datas['allname'].replace(" ", "")
                    a_code = a_code.strip()
                    a_code = a_code.replace(" ", "")
                    if a_code == datas['allname']:
                        return True, datas['soft_id']
                    else:
                        return False, 0
                else:
                    return False, 0

    @gen.coroutine
    def getProxyAccount(self, proxy_verify):
        # 查代理账号存在与否
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT account FROM proxy_account WHERE verify=%s limit 0,1" % (proxy_verify,)
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                return datas

    @gen.coroutine
    def CheckProxyAccount(self, account):
        # 查代理账号存在与否
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT account FROM proxy_account WHERE account=%s" % (account,)
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    return True
                else:
                    return False

    @gen.coroutine
    def addProxyAccount(self, web_uid, account, a_code):
        # 新增账号
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                u_flag, soft_id = yield self.CheckUserAccount(account, a_code)
                if u_flag == True:
                    p_flag = yield self.CheckProxyAccount(account)
                    if p_flag == False:
                        sql = "INSERT INTO proxy_account(uid,account,verify,soft_id) VALUES(%s,%s,1,%s)"
                        try:# print(sql)
                            yield cursor.execute(sql % (web_uid, account, soft_id))
                            yield conn.commit()
                            return 5
                        except Exception as err:
                            yield conn.rollback()
                            logging.error("[ProxyOrderModel:addProxyAccount:INSERT]: %s" % err)
                            return -1
                    else:
                        return -2
                else:
                    return -3

    @gen.coroutine
    def AddOrderList(self, order_Tuple_add):
        # 增加订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO proxy_order(orderid,proxy_from_orderid,account,stime,profit,proxy_profit,`comment`,uaid,flag) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                # print(sql)
                # logging.debug("AddOrderList:%s" % order_Tuple_add)
                try:
                    yield cursor.executemany(sql, order_Tuple_add)
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:AddOrder:INSERT]: %s" % err)
                    return False

    @gen.coroutine
    def CheckProxyInfo(self, uid):
        # 返回查询代理信息
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "SELECT * FROM proxy_users WHERE uid=%s" % (uid)
                    yield cursor.execute(sql)
                    datas = cursor.fetchall()
                    return datas
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:CheckOrderList:SELECT]: %s" % err)
                    logging.error("[ProxyOrderModel:CheckOrderList:SELECT]: %s" % sql)
                    return []

    @gen.coroutine
    def add_proxy_info(self, web_uid, uname="", iban=""):
        # 增加信息
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:#
                    if uname == "":
                        sql = "INSERT INTO proxy_users(uid,grade_id) VALUES(%s,%s)"
                        yield cursor.execute(sql % (web_uid, 3))
                    else:
                        sql = "INSERT INTO proxy_users(uid,uname,iban,grade_id) VALUES(%s,%s,%s,%s)"
                        yield cursor.execute(sql, (web_uid, uname, iban, 3))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:add_proxy_info:INSERT]: %s" % err)
                    return False

    @gen.coroutine
    def set_proxy_u_flag(self, web_uid):
        # 修改信息
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update proxy_users set flag=0 WHERE uid=%s"
                try:
                    yield cursor.execute(sql % (web_uid,))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:set_proxy_u_flag:update]: %s" % err)
                    return False

    @gen.coroutine
    def set_proxy_grade_price(self, web_uid, grade_id):
        # 修改佣金
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update proxy_users set grade_id=%s WHERE uid=%s"
                try:
                    yield cursor.execute(sql, (int(grade_id), int(web_uid)))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:set_proxy_u_flag:update]: %s" % err)
                    return False

    @gen.coroutine
    def set_proxy_info(self, web_uid, uname, iban):
        # 修改信息
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update proxy_users set uname='%s',iban='%s',flag=1 WHERE uid=%s"
                try:
                    yield cursor.execute(sql % (uname, iban, web_uid))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:set_proxy_info:update]: %s" % err)
                    return False

    @gen.coroutine
    def UpOrderList(self, order_Tuple_edit):
        # 修改订单
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "update proxy_order set stime=%s,proxy_from_orderid=%s,`comment`=%s,account=%s,profit=%s,proxy_profit=%s,flag=%s WHERE uaid=%s AND orderid=%s"
                # print(sql)
                try:#
                    yield cursor.executemany(sql, order_Tuple_edit)
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[OrderModel:UpOrder:update]: %s" % err)
                    return False

    @gen.coroutine
    def getProxyGradePrice(self):
        # 获得等级价格
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(accountTuple)
                sql = "SELECT grade_id,grade_name,grade_price FROM proxy_grade WHERE  flag = 1"
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                return datas

    @gen.coroutine
    def findProxyGradePrice(self, accountTuple):
        # 查找等级价格
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(accountTuple)
                sql = "SELECT account,grade_price FROM proxy_account_price WHERE account in %s" % (accountTuple,)
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                grade_price = []
                for account in accountTuple:
                    flag = 0
                    for data in datas:
                        if account == data['account']:
                            grade_price.append(data['grade_price'])
                            flag = 1
                            break
                    if flag == 0:
                        grade_price.append(0)
                return grade_price

    @gen.coroutine
    def FormatTuple(self, dic_vol):
        listvol = []
        for i in dic_vol:
            listvol.append(int(i))
        listvol.append(1)
        return tuple(listvol)

    # 得到单个账户的佣金列表
    @gen.coroutine
    def getProxyOrderList(self, uid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                the_stime, the_etime = yield self.getStime(page_main.get('time_type'))
                sql = "FROM proxy_account INNER JOIN proxy_order ON proxy_account.account = proxy_order.account " \
                      "WHERE proxy_account.uid = %s AND proxy_account.verify = 2  AND proxy_order.flag =1 AND proxy_account.account = %s " % (uid, page_main.get('account'))
                if page_main['time_type'].find("last") >= 0:
                    sql = sql + " AND proxy_order.stime >= %s AND proxy_order.stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND proxy_order.stime >= %s " % the_stime
                sql2 = "SELECT proxy_account.uid " + sql + " "
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT proxy_account.uid,proxy_account.account AS acco,proxy_order.proxy_profit,proxy_order.proxy_from_orderid,from_unixtime(proxy_order.stime) AS ordertime "
                sql3 = sql3 + sql + " ORDER BY proxy_order.stime DESC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 得到单个账户的佣金总计
    @gen.coroutine
    def getProxyCount2(self, uid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_stime, the_etime = yield self.getStime(page_main.get('time_type'))
                sql = "FROM proxy_account INNER JOIN proxy_order ON proxy_account.account = proxy_order.account " \
                      "WHERE proxy_account.uid = %s AND proxy_account.verify = 2  AND proxy_order.flag =1 AND proxy_account.account = %s " % (uid, page_main.get('account'))
                if page_main['time_type'].find("last") >= 0:
                    sql = sql + " AND proxy_order.stime >= %s AND proxy_order.stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND proxy_order.stime >= %s " % the_stime
                sql5 = "SELECT  Count(*) AS all_count,Sum(proxy_order.proxy_profit) AS all_profit " + sql
                yield cursor.execute(sql5)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    # datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 得到代理的佣金总计
    @gen.coroutine
    def getProxyCount(self, uid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_stime, the_etime = yield self.getStime(page_main.get('time_type'))
                sql = "FROM proxy_account INNER JOIN proxy_order ON proxy_account.account = proxy_order.account " \
                      "WHERE proxy_account.uid = %s AND proxy_account.verify = 2  AND proxy_order.flag =1 " % uid
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND proxy_account.account like '" + search + "' "
                if page_main['time_type'].find("last") >= 0:
                    sql = sql + " AND proxy_order.stime >= %s AND proxy_order.stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND proxy_order.stime >= %s " % the_stime
                sql5 = "SELECT  Count(*) AS all_count,Sum(proxy_order.profit) AS in_profit,Sum(proxy_order.proxy_profit) AS all_profit " + sql
                yield cursor.execute(sql5)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    # datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 得到所有代理的佣金总计
    @gen.coroutine
    def getProxyCountAll(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_stime, the_etime = yield self.getStime(page_main.get('time_type'))
                sql0 = "FROM proxy_users INNER JOIN proxy_account ON proxy_users.uid = proxy_account.uid INNER JOIN proxy_order ON proxy_account.account = proxy_order.account " \
                      "WHERE proxy_account.verify = 2 AND proxy_order.flag =1 "
                sql = ""
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND proxy_users.uname like '" + search + "' "
                if page_main['time_type'].find("last") >= 0:
                    sql = sql + " AND proxy_order.stime >= %s AND proxy_order.stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND proxy_order.stime >= %s " % the_stime
                sql5 = "SELECT  Count(*) AS all_count,Sum(proxy_order.profit) AS in_profit,Sum(proxy_order.proxy_profit) AS all_profit " + sql0 + sql
                yield cursor.execute(sql5)
                datas = cursor.fetchall()
                sql6 = "SELECT  Count(*) AS all_count,Sum(proxy_order.profit) AS in_profit FROM proxy_order WHERE proxy_order.flag =1 AND proxy_order.account>0 " + sql
                yield cursor.execute(sql6)
                datas2 = cursor.fetchall()
                if len(datas) > 0:
                    # datas+datas2
                    return datas+datas2
                else:
                    return []

    # 得到代理的所有账户的佣金统计
    @gen.coroutine
    def getProxyOrderCountList(self, uid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_stime, the_etime = yield self.getStime(page_main.get('time_type'))

                sql = "FROM proxy_account INNER JOIN proxy_order ON proxy_account.account = proxy_order.account " \
                      "WHERE proxy_account.uid = %s AND proxy_account.verify = 2 AND proxy_order.flag = 1 " % uid
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND proxy_account.account like '" + search + "' "
                if page_main['time_type'].find("last") >= 0:
                    sql = sql + " AND proxy_order.stime >= %s AND proxy_order.stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND proxy_order.stime >= %s " % the_stime
                sql2 = "SELECT proxy_account.uid " + sql + " GROUP BY proxy_account.account "
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT Count(*) AS t_count,proxy_account.uid,proxy_account.account AS acco,Sum(proxy_order.proxy_profit) AS sum_profit,proxy_order.flag,proxy_order.stime "
                sql3 = sql3 + sql + "GROUP BY proxy_account.account ORDER BY proxy_account.account DESC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 得到代理的所有账户的佣金统计
    @gen.coroutine
    def getProxyOrderCountListAll(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_stime, the_etime = yield self.getStime(page_main.get('time_type'))

                sql = "FROM proxy_users INNER JOIN proxy_account ON proxy_users.uid = proxy_account.uid INNER JOIN proxy_order ON proxy_account.account = proxy_order.account " \
                      "WHERE proxy_account.verify = 2 AND proxy_order.flag =1 "
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND proxy_users.uname like '" + search + "' "
                if page_main['time_type'].find("last") >= 0:
                    sql = sql + " AND proxy_order.stime >= %s AND proxy_order.stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND proxy_order.stime >= %s " % the_stime
                sql2 = "SELECT proxy_users.uid " + sql + " GROUP BY proxy_users.uid "
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT Count(*) AS t_count,proxy_users.uid,proxy_users.uname,Sum(proxy_order.profit) AS to_profit,Sum(proxy_order.proxy_profit) AS sum_profit "
                sql3 = sql3 + sql + "GROUP BY proxy_users.uid ORDER BY sum_profit DESC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    @gen.coroutine
    def getStime(self, time_type):
        import time
        from models.public.headers_model import Headers_Models
        the_stime = 0
        the_etime = 0
        H = Headers_Models()
        if time_type == "the_year":
            the_stime = yield H.getMktime("theYear")
        elif time_type == "the_month":
            the_stime = yield H.getMktime("theMonth")
        elif time_type == "the_week":
            the_stime = yield H.getMktime("theWeek")
        elif time_type == "last_week":
            the_stime = yield H.getMktime("lastWeek")
            the_etime = yield H.getMktime("lastWeekOne")
        elif time_type == "the_day":
            the_stime = yield H.getMktime("theDay")
        elif time_type == "last_month":
            the_stime = yield H.getMktime("lastMonthOne")
            the_etime = yield H.getMktime("lastMonth")
        elif time_type == "last_year":
            the_stime = yield H.getMktime("lastYearOne")
            the_etime = yield H.getMktime("lastYear")
        elif time_type == "recent_day":
            the_stime = int(time.time()) - 60 * 60 * 24
        elif time_type == "recent_week":
            the_stime = int(time.time()) - 60 * 60 * 24 * 7
        elif time_type == "recent_month":
            the_stime = int(time.time()) - 60 * 60 * 24 * 30
        elif time_type == "recent_month3":
            the_stime = int(time.time()) - 60 * 60 * 24 * 90
        elif time_type == "recent_month6":
            the_stime = int(time.time()) - 60 * 60 * 24 * 180
        elif time_type == "recent_year":
            the_stime = int(time.time()) - 60 * 60 * 24 * 365
        else:
            the_stime = 0
        return the_stime, the_etime

    # 得到代理列表
    @gen.coroutine
    def getProxyList(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                sql = "FROM proxy_users INNER JOIN proxy_grade ON proxy_users.grade_id = proxy_grade.grade_id WHERE 1=1 "
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND proxy_users.uname like '" + search + "' "
                sql2 = "SELECT proxy_users.uid " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT proxy_grade.grade_price,proxy_users.uid,proxy_users.uname,proxy_users.flag AS u_flag,proxy_users.iban "
                sql3 = sql3 + sql + " ORDER BY proxy_users.proxy_user_id DESC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 得到代理的所有账户列表
    @gen.coroutine
    def getProxyAccountList(self, uid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                sql = "FROM proxy_account WHERE proxy_account.uid = %s " % uid
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND account like '" + search + "' "
                sql2 = "SELECT uid " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT uid,account AS acco,verify,soft_id "
                sql3 = sql3 + sql + " ORDER BY proxy_account_id DESC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 得到结算列表
    @gen.coroutine
    def getProxySettlementList(self, uid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                the_stime, the_etime = yield self.getStime(page_main.get('time_type'))
                sql = "FROM proxy_settlement WHERE uid = %s " % (uid,)
                if page_main['time_type'].find("last") >= 0:
                    sql = sql + " AND stime >= %s AND stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND stime >= %s " % the_stime
                sql2 = "SELECT uid " + sql + " "
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT uid,from_unixtime(stime) AS ordertime,in_iban,amount,remarks "
                sql3 = sql3 + sql + " ORDER BY stime DESC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 得到结算总计
    @gen.coroutine
    def getProxySettlementCount(self, uid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_stime, the_etime = yield self.getStime(page_main.get('time_type'))
                sql = "FROM proxy_settlement WHERE uid = %s " % (uid,)
                if page_main['time_type'].find("last") >= 0:
                    sql = sql + " AND stime >= %s AND stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND stime >= %s " % the_stime
                sql5 = "SELECT  Count(*) AS all_count,Sum(amount) AS all_profit " + sql
                yield cursor.execute(sql5)
                datas = cursor.fetchall()
                # print(datas)
                if len(datas) > 0:
                    # datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 统计总佣金与总结算
    @gen.coroutine
    def getProxySettlementAllCount(self, uid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('count_proxy_settlement', (uid, "@out_proxy_profit", "@out_profit", "@out_amount"))
                    yield cursor.execute("select @out_proxy_profit, @out_profit, @out_amount;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    return row['@out_proxy_profit'], row['@out_profit'], row['@out_amount']
                except Exception as err:
                    logging.error("[ProxyOrderModel:getProxySettlementAllCount:update]: %s" % err)
                    return -1, -1, -1

    @gen.coroutine
    def addProxySettlement(self, web_uid, page_papa):
        # 增加结算
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:#
                    # print(page_papa)
                    if page_papa['amount'] > 0:
                        import time
                        up_date = int(time.time())
                        sql = "INSERT INTO proxy_settlement(uid,out_iban,in_iban,in_uname,stime,amount,remarks) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                        yield cursor.execute(sql, (web_uid, page_papa['out_iban'], page_papa['in_iban'], page_papa['in_uname'], up_date, page_papa['amount'], page_papa['remarks']))
                        yield conn.commit()
                        return True
                    else:
                        return False
                except Exception as err:
                    yield conn.rollback()
                    logging.error("[ProxyOrderModel:addProxySettlement:INSERT]: %s" % err)
                    return False
