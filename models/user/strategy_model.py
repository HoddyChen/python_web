#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import hashlib
import datetime
import json
import time
import pandas

import config
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel


logger = logging.getLogger('Main')
class StrategyModel():

    # 得到策略的列表
    @gen.coroutine
    def getStrategyList(self, uid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT uaid,account,ma_name,key_ma,logo_url FROM master_users WHERE uid=%s and flag_ma=1 ORDER BY uaid DESC"
                # print(sql)
                yield cursor.execute(sql, uid)
                datas = cursor.fetchall()
        return datas

    # 得到策略的列表
    @gen.coroutine
    def getStrategyListPage(self, uid, page_main, flag):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                if page_main == None or page_main.get('search') == "0" or page_main.get('search') == "":
                    sql = " FROM master_users WHERE uid=%s AND flag_ma=%s " % (uid, flag)
                else:
                    search = "%" + page_main.get('search') + "%"
                    sql = "FROM follow_view WHERE uid=%s AND flag_ma=%s AND `account` like '%s' " % (uid, flag, search)
                sql2 = "SELECT COUNT(*) as allnum " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchone()
                if allnum['allnum'] > 0:
                    start = 0 if page_main.get('start') == None else page_main.get('start')
                    length = 10 if page_main.get('length') == None else page_main.get('length')
                    sql3 = "SELECT uaid,account,ma_name,key_ma,logo_url " + sql + " ORDER BY uaid DESC limit %s, %s" % (int(start), int(length))
                    # print(sql3)
                    yield cursor.execute(sql3)
                    datas = cursor.fetchall()
                    if len(datas) > 0:
                        datas.append(allnum)
                        # print(datas)
                        return datas
                    else:
                        return []
                else:
                    return []

    # 得到策略的详细
    @gen.coroutine
    def getStrategyInfo(self, uid, uaid, key_ma):
        # print(uid, uaid, key_ma)
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                if not uaid is None:
                    sql = "SELECT uaid,account,ma_name,key_ma,logo_url,fx_comment FROM master_users WHERE uaid=%s and uid=%s"
                    yield cursor.execute(sql, (uaid, uid))
                elif not key_ma is None:
                    sql = "SELECT uaid,account,ma_name,key_ma,logo_url,fx_comment FROM master_users WHERE key_ma=%s and uid=%s"
                    yield cursor.execute(sql, (key_ma, uid))
                datas = cursor.fetchone()
        return datas

    @gen.coroutine
    def getStrategyCount(self, followid):
        # 统计
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    from models.public.headers_model import Headers_Models
                    H = Headers_Models()
                    the_year = yield H.getMktime("theYear")
                    the_month = yield H.getMktime("theMonth")
                    the_week = yield H.getMktime("theWeek")
                    yield cursor.callproc('count_follow_order', (followid, the_week, the_month, the_year,
                                                                 "@out_position_num", "@out_position_profit",
                                                                 "@out_position_order_num", "@out_today", "@out_week",
                                                                 "@out_month", "@out_year", "@out_balance", "@out_credit",
                                                                 "@out_quity", "@out_profit", "@out_all"))
                    yield cursor.execute("select @out_position_num,@out_position_profit,@out_position_order_num,"
                                         "@out_today,@out_week,@out_month,@out_year,@out_balance,@out_credit,"
                                         "@out_quity,@out_profit,@out_all;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    # print("row:%s" % row)
                    data_dict = {}
                    if row != None:
                        data_dict['out_position_num'] = (0 if row['@out_position_num'] == None else row['@out_position_num'])
                        data_dict['out_position_profit'] = (0 if row['@out_position_profit'] == None else row['@out_position_profit'])
                        data_dict['out_today'] = (0 if row['@out_today'] == None else row['@out_today'])
                        data_dict['out_week'] = (0 if row['@out_week'] == None else row['@out_week'])
                        data_dict['out_month'] = (0 if row['@out_month'] == None else row['@out_month'])
                        data_dict['out_year'] = (0 if row['@out_year'] == None else row['@out_year'])
                        data_dict['out_balance'] = (0 if row['@out_balance'] == None else row['@out_balance'])
                        data_dict['out_credit'] = (0 if row['@out_credit'] == None else row['@out_credit'])
                        data_dict['out_quity'] = (0 if row['@out_quity'] == None else row['@out_quity'])
                        data_dict['out_profit'] = (0 if row['@out_profit'] == None else row['@out_profit'])
                        data_dict['out_all'] = (0 if row['@out_all'] == None else row['@out_all'])
                        data_dict['out_position_order_num'] = row['@out_position_order_num']
                    return data_dict
                except Exception as err:
                    logger.error("[getStrategyCount] %s" % err)
                    return None

    # 得到策略的持仓品种分布
    @gen.coroutine
    def getStrategySymbol(self, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT sum(trader.num) as num_all,trader.proname,trader.t_type FROM trader WHERE trader.etime <= 0 AND trader.t_type < 2 AND trader.uaid = %s GROUP BY trader.t_type,trader.proname ORDER BY trader.proname ASC,trader.t_type ASC"
                yield cursor.execute(sql, (uaid,))
                datas = cursor.fetchall()
                # print(datas)
                if len(datas) == 0:
                    return None, None
                else:
                    symbol_list = []
                    num_list = []
                    for data in datas:
                        if data['t_type'] == 0:
                            name_str = data['proname'] + ",buy"
                        else:
                            name_str = data['proname'] + ",sell"
                        symbol_list.append(name_str)
                        num_list.append(0 if data['num_all'] == None else data['num_all'])
                    # print(symbol_list)
                    # print(num_list)
                    return symbol_list, num_list

    # 得到策略的已用/净值
    @gen.coroutine
    def getStrategyPositionRatio(self, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT users_account.account,(case when users_account.quity<=0 then 0.01 else users_account.margin*1.00/users_account.quity end) AS position_ratio " \
                      "FROM follow INNER JOIN users_account ON follow.uaid = users_account.uaid " \
                      "WHERE follow.followid = %s AND follow.follow_flag =1 " \
                      "ORDER BY position_ratio DESC limit 0,4"
                yield cursor.execute(sql, (uaid,))
                datas = cursor.fetchall()
                sql = "SELECT margin as ma_margin, quity FROM users_account WHERE uaid = %s"
                yield cursor.execute(sql, (uaid,))
                datas2 = cursor.fetchone()
                # print(datas)
                if len(datas) == 0:
                    return None, None
                else:
                    for data in datas:
                        data['position_ratio'] = data['position_ratio']*100
                    return datas, datas2

    # 得到策略的已用/净值
    @gen.coroutine
    def getCopyNetRatioList(self, followid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "FROM follow INNER JOIN users_account ON follow.uaid = users_account.uaid "
                if page_main == None or page_main.get('search') == "0" or page_main.get('search') == "":
                    sql = sql + " WHERE "
                else:
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " WHERE `account` like '%s' AND " % search
                # if page_main['type'] == "list":
                #     sql = sql + " `news_status` > 0 "
                # elif page_main['type'] == "recycle":
                #     sql = sql + " `news_status` = 0 "

                sql = sql + " follow.followid = %s AND follow.follow_flag =1 AND follow.f_flag = 1 " % (followid,)
                sql2 = "SELECT COUNT(*) as allnum " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchone()
                if allnum['allnum'] > 0:
                    start = 0 if page_main.get('start') == None else page_main.get('start')
                    length = 10 if page_main.get('length') == None else page_main.get('length')
                    sql3 = "SELECT users_account.account, users_account.balance, users_account.quity, users_account.margin, users_account.profit, users_account.credit, " \
                      "(case when users_account.quity<=0 then 0.01 else users_account.margin*1.00/users_account.quity*100 end) AS position_ratio ," \
                      "(case when (users_account.balance+users_account.credit)=0 then 0 else users_account.profit*1.00/(users_account.balance+users_account.credit)*100 end) AS profit_ratio " \
                      + sql + " ORDER BY position_ratio DESC limit %s, %s" % (int(start), int(length))
                    # print(sql3)
                    yield cursor.execute(sql3)
                    datas = cursor.fetchall()
                    if len(datas) > 0:
                        datas.append(allnum)
                        # print(datas)
                        return datas
                    else:
                        return []
                else:
                    return []

    # 得到策略的跟单列表的在线情况
    @gen.coroutine
    def getStrategyLoging(self, uaid, page_main=None):
        copyStrategy_list = yield self.getCopyList(uaid, page_main)
        M = MasterModel()
        strategy = yield M.getMasterTime(uaid)
        copy_list = []
        now_time = int(time.time())
        if strategy:
            strategy['follow_flag'] = 9
            strategy['followid'] = 0
            strategy['f_flag'] = 0
            copy_dist = {}
            if strategy['last_time'] != None or strategy['last_time'] != "null":
                try:
                    if time.mktime(strategy['last_time'].timetuple()) + config.ERROR_TIME_ONLINE < now_time:
                        # 超时
                        copy_dist['time_out'] = 0
                    else:
                        copy_dist['time_out'] = 1
                except:
                    copy_dist['time_out'] = 0
            else:
                copy_dist['time_out'] = 0
            copy_dist.update(strategy)
            copy_list.append(copy_dist)

        if len(copyStrategy_list) <= 0:
            yy = []
            yy['allnum'] = 1
            copy_list.append(yy)
            return copy_list
        else:
            for i in range(len(copyStrategy_list)-1):
                copy_dist = {}
                if copyStrategy_list[i]['last_time'] != None or copyStrategy_list[i]['last_time'] != "null":
                    try:
                        if time.mktime(copyStrategy_list[i]['last_time'].timetuple()) + config.ERROR_TIME_ONLINE < now_time:
                            # 超时
                            copy_dist['time_out'] = 0
                        else:
                            copy_dist['time_out'] = 1
                    except:
                        copy_dist['time_out'] = 0
                else:
                    copy_dist['time_out'] = 0
                copy_dist.update(copyStrategy_list[i])
                copy_list.append(copy_dist)
            copyStrategy_list[-1]['allnum'] = len(copy_list)
            copy_list.append(copyStrategy_list[-1])
            # print(copy_list)
            return copy_list

    # 得到策略的跟单列表的在线情况
    @gen.coroutine
    def getStrategyLoging_back(self, uaid, page_main=None):
        copyStrategy_list = yield self.getCopyList(uaid, page_main)
        if len(copyStrategy_list) <= 0:
            return []
        else:
            R = RedisClass()
            now_time = int(time.time())
            copy_list = []
            for i in range(len(copyStrategy_list)-1):
                copy_dist = {}
                loging = R.RH.get(config.redis_ua_socket_end_login_time + str(copyStrategy_list[i]['uaid']))
                if loging != None:
                    try:
                        if len(loging) == 19:
                            loging = time.mktime(time.strptime(loging, '%Y-%m-%d %H:%M:%S'))
                        if int(loging) + 600 < now_time:
                            # 超时
                            copy_dist['time_out'] = 0
                        else:
                            copy_dist['time_out'] = 1
                    except:
                        copy_dist['time_out'] = 0
                else:
                    copy_dist['time_out'] = 0
                copy_dist.update(copyStrategy_list[i])
                copy_list.append(copy_dist)
            copy_list.append(copyStrategy_list[-1])
            # print(copy_list)
            return copy_list

    # 得到策略的跟单列表的在线状态统计
    @gen.coroutine
    def getStrategyLogingStatus(self, uaid):
        M = MasterModel()
        copyStrategy_list = yield M.getMaterFollow(uaid)
        strategy = yield M.getMasterTime(uaid)
        now_time = int(time.time())
        copy_dist = {}
        copy_dist['expected'] = 0
        copy_dist['actual'] = 0
        for copy in copyStrategy_list:
            if copy['follow_flag'] == 1:
                copy_dist['expected'] = copy_dist['expected'] + 1
            else:
                continue
            if copy['last_time'] != None or copy['last_time'] != "null":
                try:
                    if time.mktime(copy['last_time'].timetuple()) + config.ERROR_TIME_ONLINE >= now_time:
                        copy_dist['actual'] = copy_dist['actual'] + 1
                except:
                    pass
        if strategy and (strategy['last_time'] != None or strategy['last_time'] != "null"):
            copy_dist['expected'] = copy_dist['expected'] + 1
            try:
                if time.mktime(strategy['last_time'].timetuple()) + config.ERROR_TIME_ONLINE >= now_time:
                    copy_dist['actual'] = copy_dist['actual'] + 1
            except:
                pass

        return copy_dist

    # 得到策略的跟单列表的在线状态统计
    @gen.coroutine
    def getStrategyLogingStatus_back(self, uaid):
        M = MasterModel()
        copyStrategy_list = yield M.getMaterFollow(uaid)
        R = RedisClass()
        now_time = int(time.time())
        copy_dist = {}
        copy_dist['expected'] = 0
        copy_dist['actual'] = 0
        for copy in copyStrategy_list:
            if copy['follow_flag'] == 1:
                copy_dist['expected'] = copy_dist['expected'] + 1
            else:
                continue
            loging = R.RH.get(config.redis_ua_socket_end_login_time + str(copy['uaid']))
            if loging != None:
                try:
                    if len(loging) == 19:
                        loging = time.mktime(time.strptime(loging, '%Y-%m-%d %H:%M:%S'))
                    # print(str(copy['uaid']),copy['account'],int(loging),now_time)
                    if int(loging) + 600 >= now_time:
                        copy_dist['actual'] = copy_dist['actual'] + 1
                except:
                    pass
        return copy_dist

    # 得到策略的所有账户的持仓数量列表
    @gen.coroutine
    def getStrategyPositionCountList(self, followid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT Count(*) AS count_order,follow.maxnum,follow.uaid FROM follow INNER JOIN trader ON " \
                      "follow.uaid = trader.uaid WHERE follow.followid = %s AND follow.follow_flag = 1 AND trader.etime <= 0 AND trader.t_type<6 AND trader.followid > 0 " \
                      "GROUP BY follow.uaid"
                yield cursor.execute(sql, (followid,))
                datas = cursor.fetchall()
                return datas

    # 得到策略，计算真实持仓与预期持仓
    @gen.coroutine
    def getStrategyPositionCount(self, followid):
        datas = yield self.getStrategyPositionCountList(followid)
        from models.user.order_model import OrderModel
        O = OrderModel()
        datas2 = yield O.get_PositionOrder(followid)
        M_num = len(datas2)
        num = {}
        # 应有持仓
        num['expected'] = 0
        # 真实持仓
        num['actual'] = 0
        for data in datas:
            if data['maxnum'] != None:
                if M_num > data['maxnum']:
                    num['expected'] = num['expected'] + data['maxnum']
                else:
                    num['expected'] = num['expected'] + M_num
                    num['actual'] = num['actual'] + data['count_order']
            else:
                num['expected'] = num['expected'] + M_num
                num['actual'] = num['actual'] + data['count_order']
        return num

    # 得到跟单用户的列表
    @gen.coroutine
    def getCopyList(self, followid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                # print("search:", page_main.get('search'))
                if page_main == None or page_main.get('search') == "0" or page_main.get('search') == "":
                    sql = "FROM follow_view  WHERE f_flag = 1 AND "
                else:
                    search = "%" + page_main.get('search') + "%"
                    sql = "FROM follow_view WHERE f_flag = 1 AND `account` like '%s' AND " % search
                if page_main.get('fx_flag') == None or page_main.get('fx_flag') == 9:
                    sql = sql + "`followid`=%s " % followid
                else:
                    sql = sql + "`followid`=%s AND `follow_flag` = %s " % (followid, page_main['fx_flag'])
                sql2 = "SELECT COUNT(*) as allnum " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchone()
                if allnum['allnum'] > 0:
                    start = 0 if page_main.get('start') == None else page_main.get('start')
                    length = 10 if page_main.get('length') == None else page_main.get('length')
                    sql3 = "SELECT uaid,follow_flag,followid,f_flag,account,allname,last_time " + sql + " ORDER BY uaid DESC limit %s, %s" % (int(start), int(length))
                    # print(sql3)
                    yield cursor.execute(sql3)
                    datas = cursor.fetchall()
                    if len(datas) > 0:
                        datas.append(allnum)
                        # print(datas)
                        return datas
                    else:
                        return []
                else:
                    return []



    # 得到跟单账户的持仓情况
    @gen.coroutine
    def getStrategyPositionList(self, uaid, page_main=None):
        copyStrategy_list = yield self.getCopyPositionList(uaid, page_main)
        from models.user.order_model import OrderModel
        O = OrderModel()
        datas2 = yield O.get_PositionOrder(uaid)
        M_num = len(datas2)
        for i in range(len(copyStrategy_list)-1):
            if not copyStrategy_list[i]['order_lots']:
                copyStrategy_list[i]['order_num'] = 0
            copyStrategy_list[i]['M_num'] = M_num
            if copyStrategy_list[i]['order_num'] == M_num:
                copyStrategy_list[i]['num_flag'] = 1
            else:
                copyStrategy_list[i]['maxnum'] = 5 if copyStrategy_list[i]['maxnum'] == None else copyStrategy_list[i]['maxnum']
                if M_num > copyStrategy_list[i]['maxnum'] and copyStrategy_list[i]['order_num'] == copyStrategy_list[i]['maxnum']:
                    copyStrategy_list[i]['num_flag'] = 1
                else:
                    copyStrategy_list[i]['num_flag'] = 0
        # print(copyStrategy_list)
        return copyStrategy_list

    # 得到跟单账户的持仓情况
    @gen.coroutine
    def getCopyPositionList(self, followid, page_main=None):
        # from models.user.order_model import OrderModel
        # O = OrderModel()
        # datas2 = yield O.get_PositionOrder(followid)
        # M_num = len(datas2)
        # print(M_num)
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                # print("search:",page_main.get('search'))
                sql = "FROM follow LEFT JOIN trader ON follow.uaid = trader.uaid AND trader.etime <= 0 AND " \
                      "trader.followid > 0 AND trader.t_type < 6 INNER JOIN users_account ON follow.uaid = users_account.uaid "
                if page_main == None or page_main.get('search') == "0" or page_main.get('search') == "":
                    sql = sql + "WHERE "
                else:
                    search = "%" + page_main.get('search') + "%"
                    # sql = "FROM follow INNER JOIN users_account ON follow.uaid = users_account.uaid INNER JOIN " \
                    #       "trader ON follow.uaid = trader.uaid WHERE `account` like '%s' AND " % search
                    sql = sql + "WHERE `account` like '%s' AND " % search
                sql = sql + " follow.followid = %s AND follow.follow_flag = 1 AND follow.f_flag = 1 GROUP BY follow.uaid " % followid
                sql2 = "SELECT follow.uaid " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT Count(*) AS order_num,follow.uaid,users_account.account,users_account.credit," \
                       "follow.maxnum,users_account.balance,users_account.quity AS equity,users_account.margin," \
                       "users_account.profit,SUM(trader.num) AS order_lots "\
                       + sql + " ORDER BY order_num ASC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []
                # print(datas)

    # 修改授权
    @gen.coroutine
    def edit_authorization(self, uid, ip, followid, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('edit_mater_authorize', (uid, ip, config.PID, followid, uaid, "@out_mflag"))
                    yield cursor.execute("select @out_mflag;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    # print("edit_authorization:", row)
                    if row['@out_mflag'] >= 0:
                        from handlers.myredis.redis_class import RedisClass
                        R = RedisClass()
                        # R.RH.hset(config.redis_master_uaid_Hash + str(followid), str(uaid), row['@out_mflag'])
                        yield R.set_MaterFollow(str(followid), str(uaid), row['@out_mflag'])

                    return row['@out_mflag']
                except Exception as err:
                    # print("[edit_authorization] %s" % err)
                    return -1

    # 获得参数
    @gen.coroutine
    def getParameter(self, followid, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # sql = "SELECT follow.maxloss,follow.maxtime,follow.maxnum,follow.fixed,follow.percent,follow.rate," \
                #       "follow.rate_max,follow.rate_min,follow.reflex,follow.allowed_sign,follow.update_time,follow.parameter_time," \
                #       "product_info.info10,product_info.info11,product_info.info12,product_info.info13 " \
                #       "FROM follow " \
                #       "INNER JOIN p_order ON follow.followid = p_order.uaid " \
                #       "INNER JOIN product_info ON p_order.piid = product_info.piid " \
                #       "WHERE follow.followid = %s AND follow.uaid = %s AND product_info.pid = %s " \
                #       "AND p_order.strattime < now() AND p_order.endtime > now() AND p_order.otype = 1 " \
                #       "ORDER BY p_order.piid DESC LIMIT 1"
                sql = "SELECT follow.maxloss,follow.maxtime,follow.maxnum,follow.fixed,follow.percent,follow.rate,follow.rate_max,follow.rate_min,follow.reflex,follow.allowed_sign,follow.tpsl_flag,follow.pending_flag,follow.update_time,follow.parameter_time,product_info.info10,product_info.info11,product_info.info12,product_info.info13,users_account.minlot,users_account.maxlot " \
                      "FROM follow " \
                      "INNER JOIN p_order ON follow.followid = p_order.uaid " \
                      "INNER JOIN product_info ON p_order.piid = product_info.piid " \
                      "INNER JOIN users_account ON follow.uaid = users_account.uaid " \
                      "WHERE follow.followid = %s AND follow.uaid = %s AND product_info.pid = %s AND p_order.strattime < now() AND p_order.endtime > now() AND p_order.otype = 1 " \
                      "ORDER BY product_info.info10 DESC LIMIT 1"
                # print(sql % (followid, uaid, config.PID))
                yield cursor.execute(sql, (followid, uaid, config.PID))
                row = cursor.fetchone()
                return row

    # 得到策略的所有跟单账户的手数、单量、盈利的统计
    @gen.coroutine
    def getCopyOrderCountList(self, followid, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_etime = 0
                if page_main != None:
                    from models.public.headers_model import Headers_Models
                    H = Headers_Models()
                    if page_main['time_type'] == "the_year":
                        the_stime = yield H.getMktime("theYear")
                    elif page_main['time_type'] == "the_month":
                        the_stime = yield H.getMktime("theMonth")
                    elif page_main['time_type'] == "the_week":
                        the_stime = yield H.getMktime("theWeek")
                    elif page_main['time_type'] == "the_day":
                        the_stime = yield H.getMktime("theDay")
                    elif page_main['time_type'] == "last_month":
                        the_stime = yield H.getMktime("lastMonthOne")
                        the_etime = yield H.getMktime("lastMonth")
                    elif page_main['time_type'] == "last_year":
                        the_stime = yield H.getMktime("lastYearOne")
                        the_etime = yield H.getMktime("lastYear")
                    elif page_main['time_type'] == "recent_day":
                        the_stime = int(time.time()) - 60 * 60 * 24
                    elif page_main['time_type'] == "recent_week":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 7
                    elif page_main['time_type'] == "recent_month":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 30
                    elif page_main['time_type'] == "recent_month3":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 90
                    elif page_main['time_type'] == "recent_month6":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 180
                    elif page_main['time_type'] == "recent_year":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 365
                    else:
                        the_stime = 0
                sql = "FROM follow INNER JOIN trader ON follow.uaid = trader.uaid INNER JOIN users_account ON follow.uaid = users_account.uaid " \
                       "WHERE follow.followid = %s AND follow.follow_flag = 1 AND follow.f_flag = 1 " % followid
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND users_account.account like '" + search + "' "
                if the_etime != 0:
                    sql = sql + " AND trader.etime >= %s AND trader.etime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND trader.etime >= %s " % the_stime
                sql2 = "SELECT follow.uaid " + sql + " GROUP BY follow.uaid "
                # print(sql2)
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()
                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 10 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT Count(*) AS t_count,Sum(trader.num) AS t_num,Sum(trader.profit) AS t_profit,Sum(trader.swap) AS t_swap," \
                      "Sum(trader.commission) AS t_comm,follow.uaid,users_account.account,users_account.allname "
                sql3 = sql3 + sql + " GROUP BY follow.uaid ORDER BY follow.fid DESC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    return datas
                else:
                    return []

    # 修改策略名称
    @gen.coroutine
    def edit_info(self, uid, ip, ma_name, url, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('edit_master_info', (uid, ip, ma_name, url, uaid, "@out_mflag"))
                    yield cursor.execute("select @out_mflag;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    if row['@out_mflag'] == 5 and url != None:
                        self.set_secure_cookie("current_logo_url" + uid, url)
                    # print("edit_master_info:", row)
                    return row['@out_mflag']
                except Exception as err:
                    # print("[edit_master_info] %s" % err)
                    return -1

    # 修改策略订单备注
    @gen.coroutine
    def edit_info_comment(self, uid, ip, comment, current_key_ma, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('edit_master_info_comment', (uid, ip, comment, None, uaid, "@out_mflag"))
                    yield cursor.execute("select @out_mflag;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    if row['@out_mflag'] == 5 and current_key_ma != None:
                        R = RedisClass()
                        R.insert_master_Comment(current_key_ma, comment)
                        # R.get_Mater_Comment(current_key_ma)
                    return row['@out_mflag']
                except Exception as err:
                    # print("[edit_master_info] %s" % err)
                    return -1

    # 修改策略有效标志
    @gen.coroutine
    def edit_master_delete(self, uid, ip, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('edit_master_delete', (uid, ip, uaid, "@out_mflag"))
                    yield cursor.execute("select @out_mflag;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    return row['@out_mflag']
                except Exception as err:
                    # print("[edit_master_info] %s" % err)
                    return -1


    # 修改跟单账号有效标志
    @gen.coroutine
    def edit_follow_delete(self, follow_id, uid, ip, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('edit_follow_falg', (follow_id, uid, ip, uaid, "@out_mflag"))
                    yield cursor.execute("select @out_mflag;")
                    # for result in cursor.stored_results():
                    #     print(result.fetchall())
                    row = cursor.fetchone()
                    return row['@out_mflag']
                except Exception as err:
                    # print("[edit_master_info] %s" % err)
                    return -1


    # 修改对外展示
    @gen.coroutine
    def edit_url_key(self, ip, pu_status, urlpass, uaid, urlkey):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('edit_proxy_url', (ip, pu_status, urlpass, uaid, urlkey, "@out_mflag", "@out_url_key"))
                    yield cursor.execute("select @out_mflag,@out_url_key;")
                    row = cursor.fetchone()
                    # print(row)
                    if row:
                        if row['@out_mflag'] >= 5:
                            return row
                        else:
                            return -2
                    else:
                        return -3
                except Exception as err:
                    # print("[edit_master_info] %s" % err)
                    return -1

    # 获得
    @gen.coroutine
    def getProxyUrl(self, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT url_key,url_pass,pu_status FROM proxy_url WHERE uaid = %s"
                yield cursor.execute(sql, (uaid,))
                row = cursor.fetchone()
                return row

    # 获得跟单账户的策略详情
    @gen.coroutine
    def getUrlStrategy(self, urlkey, fx_pass):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT master_account.ma_name,master_account.logo_url,users_account.account,users_account.moni,platfrom.ptname,plat_server.accountserver,follow.followid " \
                      "FROM proxy_url INNER JOIN follow ON proxy_url.uaid = follow.uaid " \
                      "INNER JOIN master_account ON follow.followid = master_account.uaid " \
                      "INNER JOIN users_account ON proxy_url.uaid = users_account.uaid " \
                      "INNER JOIN plat_server ON users_account.pfuid = plat_server.pfuid " \
                      "INNER JOIN platfrom ON users_account.pt_id = platfrom.pt_id " \
                      "WHERE proxy_url.url_key=%s AND proxy_url.url_pass=%s AND proxy_url.pu_status=1 AND follow.follow_flag=1 " \
                      "ORDER BY follow.followid DESC limit 0, 1"
                # print(sql % (urlkey, fx_pass))
                yield cursor.execute(sql, (urlkey, fx_pass))
                datas = cursor.fetchone()
                return datas

    # 获得策略账户的策略详情
    @gen.coroutine
    def getUaidStrategy(self, urlkey, fx_pass):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT master_account.ma_name,master_account.logo_url,users_account.account,platfrom.ptname,plat_server.accountserver,proxy_url.uaid AS followid,users_account.moni " \
                      "FROM proxy_url INNER JOIN master_account ON proxy_url.uaid = master_account.uaid " \
                      "INNER JOIN users_account ON master_account.uaid = users_account.uaid " \
                      "INNER JOIN platfrom ON users_account.pt_id = platfrom.pt_id " \
                      "INNER JOIN plat_server ON users_account.pfuid = plat_server.pfuid " \
                      "WHERE proxy_url.url_key=%s AND proxy_url.url_pass=%s AND proxy_url.pu_status=1 " \
                      "limit 0, 1"
                # print(sql % (urlkey, fx_pass))
                yield cursor.execute(sql, (urlkey, fx_pass))
                datas = cursor.fetchone()
                return datas

    # 通过id获得策略账户的策略详情
    @gen.coroutine
    def getfollowidStrategy(self, followid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT master_account.ma_name,master_account.logo_url,users_account.account,platfrom.ptname," \
                      "plat_server.accountserver,master_account.uaid AS followid,users_account.moni " \
                      "FROM master_account" \
                      "	INNER JOIN users_account ON master_account.uaid = users_account.uaid" \
                      "	INNER JOIN platfrom ON users_account.pt_id = platfrom.pt_id" \
                      "	INNER JOIN plat_server ON users_account.pfuid = plat_server.pfuid " \
                      "WHERE master_account.uaid = %s LIMIT 0,1"
                # print(sql % (urlkey, fx_pass))
                yield cursor.execute(sql, (followid))
                datas = cursor.fetchone()
                return datas

    # 得到uaid对应的账户号
    @gen.coroutine
    def getAccount(self, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT users_account.account FROM users_account WHERE uaid=%s"
                yield cursor.execute(sql, (uaid,))
                row = cursor.fetchone()
                return row

    # 判断是否有查看权限
    @gen.coroutine
    def chickUrlKey(self, urlkey, fx_pass):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT uaid FROM proxy_url WHERE url_key = %s AND url_pass = %s AND pu_status=1"
                yield cursor.execute(sql, (urlkey, fx_pass))
                row = cursor.fetchone()
                if row:
                    # 查是不是策略
                    from models.user.master_model import MasterModel
                    M = MasterModel()
                    data = yield M.getMaterInfo(row['uaid'], config.PID)
                    if data['endtime'] == None or data['endtime'] < datetime.datetime.now():
                        s_data = yield self.getUrlStrategy(urlkey, fx_pass)
                        if s_data == None:
                            return None
                        else:
                            data2 = yield M.getMaterInfo(s_data['followid'], config.PID)
                            if data2['endtime'] == None or data2['endtime'] < datetime.datetime.now():
                                return None
                            else:
                                data2['uaid'] = row['uaid']
                                return data2
                    else:
                        data['uaid'] = row['uaid']
                        return data
                else:
                    return None

    # 获得历史记录
    @gen.coroutine
    def getHistoryOrderList(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                the_etime = 0
                if page_main != None:
                    from models.public.headers_model import Headers_Models
                    H = Headers_Models()
                    if page_main['time_type'] == "the_year":
                        the_stime = yield H.getMktime("theYear")
                    elif page_main['time_type'] == "the_month":
                        the_stime = yield H.getMktime("theMonth")
                    elif page_main['time_type'] == "the_week":
                        the_stime = yield H.getMktime("theWeek")
                    elif page_main['time_type'] == "the_day":
                        the_stime = yield H.getMktime("theDay")
                    elif page_main['time_type'] == "last_month":
                        the_stime = yield H.getMktime("lastMonthOne")
                        the_etime = yield H.getMktime("lastMonth")
                    elif page_main['time_type'] == "last_year":
                        the_stime = yield H.getMktime("lastYearOne")
                        the_etime = yield H.getMktime("lastYear")
                    elif page_main['time_type'] == "recent_day":
                        the_stime = int(time.time()) - 60 * 60 * 24
                    elif page_main['time_type'] == "recent_week":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 7
                    elif page_main['time_type'] == "recent_month":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 30
                    elif page_main['time_type'] == "recent_month3":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 90
                    elif page_main['time_type'] == "recent_month6":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 180
                    elif page_main['time_type'] == "recent_year":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 365
                    else:
                        the_stime = 0
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                # print("search:", page_main.get('search'))
                sql = "FROM trader WHERE "
                sql = sql + "(etime > 0 OR t_type>=6) AND uaid=%s " % page_main['uaid']
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND trader.proname like '" + search + "' "
                if the_etime != 0:
                    sql = sql + " AND trader.etime >= %s AND trader.etime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND trader.etime >= %s " % the_stime
                sql2 = "SELECT COUNT(*) as allnum " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchone()
                if allnum['allnum'] > 0:
                    start = 0 if page_main.get('start') == None else page_main.get('start')
                    length = 10 if page_main.get('length') == None else page_main.get('length')
                    sql3 = "SELECT trader.orderid,trader.proname,trader.num,trader.t_type,FROM_UNIXTIME(trader.stime,'%Y-%m-%d %H:%i:%s') AS from_stime,trader.sprice,FROM_UNIXTIME(trader.etime,'%Y-%m-%d %H:%i:%s') AS from_etime,trader.eprice,trader.sl,trader.tp,trader.commission,trader.swap,trader.profit " + sql + " ORDER BY orderid DESC limit %s, %s" % (int(start), int(length))
                    # print(sql3)
                    yield cursor.execute(sql3)
                    datas = cursor.fetchall()
                    if len(datas) > 0:
                        datas.append(allnum)
                        # print(datas)
                        return datas
                    else:
                        return []
                else:
                    return []

    # 得到账户统计报告的手数、单量、盈利的统计
    @gen.coroutine
    def getHistoryReportCount(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_etime = 0
                if page_main != None:
                    from models.public.headers_model import Headers_Models
                    H = Headers_Models()
                    if page_main['time_type'] == "the_year":
                        the_stime = yield H.getMktime("theYear")
                    elif page_main['time_type'] == "the_month":
                        the_stime = yield H.getMktime("theMonth")
                    elif page_main['time_type'] == "the_week":
                        the_stime = yield H.getMktime("theWeek")
                    elif page_main['time_type'] == "the_day":
                        the_stime = yield H.getMktime("theDay")
                    elif page_main['time_type'] == "last_month":
                        the_stime = yield H.getMktime("lastMonthOne")
                        the_etime = yield H.getMktime("lastMonth")
                    elif page_main['time_type'] == "last_year":
                        the_stime = yield H.getMktime("lastYearOne")
                        the_etime = yield H.getMktime("lastYear")
                    elif page_main['time_type'] == "recent_day":
                        the_stime = int(time.time()) - 60 * 60 * 24
                    elif page_main['time_type'] == "recent_week":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 7
                    elif page_main['time_type'] == "recent_month":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 30
                    elif page_main['time_type'] == "recent_month3":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 90
                    elif page_main['time_type'] == "recent_month6":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 180
                    elif page_main['time_type'] == "recent_year":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 365
                    else:
                        the_stime = 0
                sql = "FROM trader WHERE "
                sql = sql + " uaid=%s AND trader.t_type<=1 " % page_main['uaid']
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND trader.proname like '" + search + "' "
                # if page_main['time_type'].find("last") >= 0:
                if the_etime != 0:
                    sql = sql + " AND trader.etime >= %s AND trader.etime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND trader.etime >= %s " % the_stime
                sql2 = "SELECT Count(*) AS t_count,Sum(trader.num) AS t_num,Sum(trader.profit) AS t_profit,Sum(trader.swap) AS t_swap," \
                      "Sum(trader.commission) AS t_comm,Max(trader.profit) AS t_maxprofit,Min(trader.profit) AS t_minprofit,AVG(trader.profit) AS t_avgprofit," \
                       " Max(trader.maxprofit) AS t_maxfloat,Min(trader.minprofit) AS t_minfloat " + sql
                sql3 = sql2 + " AND trader.profit>=0"
                #print(sql3)
                sql4 = sql2 + " AND trader.profit<0"
                sql5 = sql2 + " AND trader.t_type=0 AND trader.profit>=0"
                sql6 = sql2 + " AND trader.t_type=0 AND trader.profit<0"
                sql7 = sql2 + " AND trader.t_type=1 AND trader.profit>=0"
                sql8 = sql2 + " AND trader.t_type=1 AND trader.profit<0"
                # print(sql2)
                yield cursor.execute(sql3)
                datas3 = cursor.fetchall()
                yield cursor.execute(sql4)
                datas4 = cursor.fetchall()
                yield cursor.execute(sql5)
                datas5 = cursor.fetchall()
                yield cursor.execute(sql6)
                datas6 = cursor.fetchall()
                yield cursor.execute(sql7)
                datas7 = cursor.fetchall()
                yield cursor.execute(sql8)
                datas8 = cursor.fetchall()

                datas3[0]['t_count'] = 0 if datas3[0]['t_count'] == None else datas3[0]['t_count']
                datas3[0]['t_num'] = 0 if datas3[0]['t_num'] == None else datas3[0]['t_num']
                datas3[0]['t_profit'] = 0 if datas3[0]['t_profit'] == None else datas3[0]['t_profit']
                datas3[0]['t_swap'] = 0 if datas3[0]['t_swap'] == None else datas3[0]['t_swap']
                datas3[0]['t_comm'] = 0 if datas3[0]['t_comm'] == None else datas3[0]['t_comm']
                datas3[0]['t_maxprofit'] = 0 if datas3[0]['t_maxprofit'] == None else datas3[0]['t_maxprofit']
                datas3[0]['t_minprofit'] = 0 if datas3[0]['t_minprofit'] == None else datas3[0]['t_minprofit']
                datas3[0]['t_avgprofit'] = 0 if datas3[0]['t_avgprofit'] == None else datas3[0]['t_avgprofit']
                datas3[0]['t_minprofit'] = 0 if datas3[0]['t_minprofit'] == None else datas3[0]['t_minprofit']
                datas3[0]['t_maxfloat'] = 0 if datas3[0]['t_maxfloat'] == None else datas3[0]['t_maxfloat']
                datas3[0]['t_minfloat'] = 0 if datas3[0]['t_minfloat'] == None else datas3[0]['t_minfloat']

                datas4[0]['t_count'] = 0 if datas4[0]['t_count'] == None else datas4[0]['t_count']
                datas4[0]['t_num'] = 0 if datas4[0]['t_num'] == None else datas4[0]['t_num']
                datas4[0]['t_profit'] = 0 if datas4[0]['t_profit'] == None else datas4[0]['t_profit']
                datas4[0]['t_swap'] = 0 if datas4[0]['t_swap'] == None else datas4[0]['t_swap']
                datas4[0]['t_comm'] = 0 if datas4[0]['t_comm'] == None else datas4[0]['t_comm']
                datas4[0]['t_maxprofit'] = 0 if datas4[0]['t_maxprofit'] == None else datas4[0]['t_maxprofit']
                datas4[0]['t_minprofit'] = 0 if datas4[0]['t_minprofit'] == None else datas4[0]['t_minprofit']
                datas4[0]['t_avgprofit'] = 0 if datas4[0]['t_avgprofit'] == None else datas4[0]['t_avgprofit']
                datas4[0]['t_minprofit'] = 0 if datas4[0]['t_minprofit'] == None else datas4[0]['t_minprofit']
                datas4[0]['t_maxfloat'] = 0 if datas4[0]['t_maxfloat'] == None else datas4[0]['t_maxfloat']
                datas4[0]['t_minfloat'] = 0 if datas4[0]['t_minfloat'] == None else datas4[0]['t_minfloat']

                datas5[0]['t_count'] = 0 if datas5[0]['t_count'] == None else datas5[0]['t_count']
                datas5[0]['t_num'] = 0 if datas5[0]['t_num'] == None else datas5[0]['t_num']
                datas5[0]['t_profit'] = 0 if datas5[0]['t_profit'] == None else datas5[0]['t_profit']
                datas5[0]['t_swap'] = 0 if datas5[0]['t_swap'] == None else datas5[0]['t_swap']
                datas5[0]['t_comm'] = 0 if datas5[0]['t_comm'] == None else datas5[0]['t_comm']
                datas5[0]['t_maxprofit'] = 0 if datas5[0]['t_maxprofit'] == None else datas5[0]['t_maxprofit']
                datas5[0]['t_minprofit'] = 0 if datas5[0]['t_minprofit'] == None else datas5[0]['t_minprofit']
                datas5[0]['t_avgprofit'] = 0 if datas5[0]['t_avgprofit'] == None else datas5[0]['t_avgprofit']
                datas5[0]['t_minprofit'] = 0 if datas5[0]['t_minprofit'] == None else datas5[0]['t_minprofit']
                datas5[0]['t_maxfloat'] = 0 if datas5[0]['t_maxfloat'] == None else datas5[0]['t_maxfloat']
                datas5[0]['t_minfloat'] = 0 if datas5[0]['t_minfloat'] == None else datas5[0]['t_minfloat']

                datas6[0]['t_count'] = 0 if datas6[0]['t_count'] == None else datas6[0]['t_count']
                datas6[0]['t_num'] = 0 if datas6[0]['t_num'] == None else datas6[0]['t_num']
                datas6[0]['t_profit'] = 0 if datas6[0]['t_profit'] == None else datas6[0]['t_profit']
                datas6[0]['t_swap'] = 0 if datas6[0]['t_swap'] == None else datas6[0]['t_swap']
                datas6[0]['t_comm'] = 0 if datas6[0]['t_comm'] == None else datas6[0]['t_comm']
                datas6[0]['t_maxprofit'] = 0 if datas6[0]['t_maxprofit'] == None else datas6[0]['t_maxprofit']
                datas6[0]['t_minprofit'] = 0 if datas6[0]['t_minprofit'] == None else datas6[0]['t_minprofit']
                datas6[0]['t_avgprofit'] = 0 if datas6[0]['t_avgprofit'] == None else datas6[0]['t_avgprofit']
                datas6[0]['t_minprofit'] = 0 if datas6[0]['t_minprofit'] == None else datas6[0]['t_minprofit']
                datas6[0]['t_maxfloat'] = 0 if datas6[0]['t_maxfloat'] == None else datas6[0]['t_maxfloat']
                datas6[0]['t_minfloat'] = 0 if datas6[0]['t_minfloat'] == None else datas6[0]['t_minfloat']

                datas7[0]['t_count'] = 0 if datas7[0]['t_count'] == None else datas7[0]['t_count']
                datas7[0]['t_num'] = 0 if datas7[0]['t_num'] == None else datas7[0]['t_num']
                datas7[0]['t_profit'] = 0 if datas7[0]['t_profit'] == None else datas7[0]['t_profit']
                datas7[0]['t_swap'] = 0 if datas7[0]['t_swap'] == None else datas7[0]['t_swap']
                datas7[0]['t_comm'] = 0 if datas7[0]['t_comm'] == None else datas7[0]['t_comm']
                datas7[0]['t_maxprofit'] = 0 if datas7[0]['t_maxprofit'] == None else datas7[0]['t_maxprofit']
                datas7[0]['t_minprofit'] = 0 if datas7[0]['t_minprofit'] == None else datas7[0]['t_minprofit']
                datas7[0]['t_avgprofit'] = 0 if datas7[0]['t_avgprofit'] == None else datas7[0]['t_avgprofit']
                datas7[0]['t_minprofit'] = 0 if datas7[0]['t_minprofit'] == None else datas7[0]['t_minprofit']
                datas7[0]['t_maxfloat'] = 0 if datas7[0]['t_maxfloat'] == None else datas7[0]['t_maxfloat']
                datas7[0]['t_minfloat'] = 0 if datas7[0]['t_minfloat'] == None else datas7[0]['t_minfloat']

                datas8[0]['t_count'] = 0 if datas8[0]['t_count'] == None else datas8[0]['t_count']
                datas8[0]['t_num'] = 0 if datas8[0]['t_num'] == None else datas8[0]['t_num']
                datas8[0]['t_profit'] = 0 if datas8[0]['t_profit'] == None else datas8[0]['t_profit']
                datas8[0]['t_swap'] = 0 if datas8[0]['t_swap'] == None else datas8[0]['t_swap']
                datas8[0]['t_comm'] = 0 if datas8[0]['t_comm'] == None else datas8[0]['t_comm']
                datas8[0]['t_maxprofit'] = 0 if datas8[0]['t_maxprofit'] == None else datas8[0]['t_maxprofit']
                datas8[0]['t_minprofit'] = 0 if datas8[0]['t_minprofit'] == None else datas8[0]['t_minprofit']
                datas8[0]['t_avgprofit'] = 0 if datas8[0]['t_avgprofit'] == None else datas8[0]['t_avgprofit']
                datas8[0]['t_minprofit'] = 0 if datas8[0]['t_minprofit'] == None else datas8[0]['t_minprofit']
                datas8[0]['t_maxfloat'] = 0 if datas8[0]['t_maxfloat'] == None else datas8[0]['t_maxfloat']
                datas8[0]['t_minfloat'] = 0 if datas8[0]['t_minfloat'] == None else datas8[0]['t_minfloat']

                sql9 = "SELECT FROM_UNIXTIME(etime,'%Y-%m-%d') AS d_time,Sum(profit+swap+commission) AS t_profit " \
                       "FROM trader WHERE  etime > 0 AND t_type<=1 AND uaid=" + str(page_main['uaid']) + " GROUP BY d_time "
                yield cursor.execute(sql9)
                datas9 = cursor.fetchall()
                pd_date = pandas.DataFrame(list(datas9))
                datas = {}
                datas['sharpe_ratio_3'], datas['sharpe_ratio_0'] = yield self.getSharpeRatio(pd_date)
                # print(datas4)
                # print(datas5)
                # print(datas6)
                datas['t_profit'] = datas3[0]['t_profit'] + datas3[0]['t_swap'] + datas3[0]['t_comm'] + datas4[0]['t_profit'] + datas4[0]['t_swap'] + datas4[0]['t_comm']
                datas['t_profit_2'] = datas4[0]['t_profit'] + datas4[0]['t_swap'] + datas4[0]['t_comm']
                datas['t_profit_1'] = datas3[0]['t_profit'] + datas3[0]['t_swap'] + datas3[0]['t_comm']
                datas['t_count'] = datas3[0]['t_count'] + datas4[0]['t_count']
                datas['t_count0'] = datas3[0]['t_count']
                datas['t_count1'] = datas4[0]['t_count']
                datas['t_num'] = datas3[0]['t_num'] + datas4[0]['t_num']
                datas['t_num0'] = datas3[0]['t_num']
                datas['t_num1'] = datas4[0]['t_num']
                datas['t_maxprofit'] = datas3[0]['t_maxprofit']
                datas['t_maxfloat'] = datas3[0]['t_maxfloat']
                datas['t_minprofit'] = datas4[0]['t_minprofit']
                datas['t_minfloat'] = datas4[0]['t_minfloat']
                datas['t_avgprofit0'] = datas3[0]['t_avgprofit']
                datas['t_avgprofit1'] = datas4[0]['t_avgprofit']

                datas['t0_profit'] = datas5[0]['t_profit'] + datas5[0]['t_swap'] + datas5[0]['t_comm'] + datas6[0][
                    't_profit'] + datas6[0]['t_swap'] + datas6[0]['t_comm']
                datas['t0_profit_1'] = datas5[0]['t_profit'] + datas5[0]['t_swap'] + datas5[0]['t_comm']
                datas['t0_profit_2'] = datas6[0]['t_profit'] + datas6[0]['t_swap'] + datas6[0]['t_comm']
                datas['t0_count'] = datas5[0]['t_count'] + datas6[0]['t_count']
                datas['t0_count0'] = datas5[0]['t_count']
                datas['t0_count1'] = datas6[0]['t_count']
                datas['t0_num'] = datas5[0]['t_num'] + datas6[0]['t_num']
                datas['t0_num0'] = datas5[0]['t_num']
                datas['t0_num1'] = datas6[0]['t_num']
                datas['t0_maxprofit'] = datas5[0]['t_maxprofit']
                datas['t0_maxfloat'] = datas5[0]['t_maxfloat']
                datas['t0_minprofit'] = datas6[0]['t_minprofit']
                datas['t0_minfloat'] = datas6[0]['t_minfloat']
                datas['t0_avgprofit0'] = datas5[0]['t_avgprofit']
                datas['t0_avgprofit1'] = datas6[0]['t_avgprofit']

                datas['t1_profit'] = datas7[0]['t_profit'] + datas7[0]['t_swap'] + datas7[0]['t_comm'] + datas8[0][
                    't_profit'] + datas8[0]['t_swap'] + datas8[0]['t_comm']
                datas['t1_profit_1'] = datas7[0]['t_profit'] + datas7[0]['t_swap'] + datas7[0]['t_comm']
                datas['t1_profit_2'] = datas8[0]['t_profit'] + datas8[0]['t_swap'] + datas8[0]['t_comm']
                datas['t1_count'] = datas7[0]['t_count'] + datas8[0]['t_count']
                datas['t1_count0'] = datas7[0]['t_count']
                datas['t1_count1'] = datas8[0]['t_count']
                datas['t1_num'] = datas7[0]['t_num'] + datas8[0]['t_num']
                datas['t1_num0'] = datas7[0]['t_num']
                datas['t1_num1'] = datas8[0]['t_num']
                datas['t1_maxprofit'] = datas7[0]['t_maxprofit']
                datas['t1_maxfloat'] = datas7[0]['t_maxfloat']
                datas['t1_minprofit'] = datas8[0]['t_minprofit']
                datas['t1_minfloat'] = datas8[0]['t_minfloat']
                datas['t1_avgprofit0'] = datas7[0]['t_avgprofit']
                datas['t1_avgprofit1'] = datas8[0]['t_avgprofit']
                datas10 = yield self.getFunds(page_main['uaid'], the_stime, the_etime)
                datas.update(datas10)
                # print(datas)
                return [datas]

    #夏普比率
    @gen.coroutine
    def getSharpeRatio(self, pandas_order, Risk_free_interest=0.03, indextype=False):
        import math
        Risk_free_interest = math.pow(1 + Risk_free_interest, 1/365) - 1
        if indextype == True:
            pandas_order['d_time'] = pandas.to_datetime(pandas_order['d_time'])  # 将数据类型转换为日期类型
            pandas_order = pandas_order.set_index('d_time')  # 将date设置为index
        pandas_order['Equity'] = pandas_order['t_profit'].cumsum()
        # pandas_orderProfit = pandas_order[['Equity']].resample('D').last().dropna()
        # pandas_orderInvest = pandas_orderProfit[pandas_orderProfit['Profit']!=0]
        # pandas_orderInvest = pandas_orderInvest+1000000
        pandas_order['daily_return'] = pandas_order['Equity'].pct_change(1)
        mean = pandas_order['daily_return'].mean()
        std = pandas_order['daily_return'].std()
        sr1 = (mean - Risk_free_interest) / std * math.sqrt(252)
        sr2 = mean / std * math.sqrt(252)
        # print(" ")
        # print("夏普比率: \t%.2f(3) \t%.2f(0)" % (sr1, sr2))
        # pandas_orderEquity = pandas_order[['Equity']].resample('D').first()
        # pandas_ = pd.concat([pandas_orderProfit, pandas_orderEquity], axis=1).dropna()
        # print("")
        # print(type(sr1))
        if math.isnan(sr1):
            sr1 = 0
        if math.isnan(sr2):
            sr2 = 0
        return sr1, sr2

    # 得到账户的手数、单量、盈利的统计
    @gen.coroutine
    def getHistoryCount(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_etime = 0
                if page_main != None:
                    from models.public.headers_model import Headers_Models
                    H = Headers_Models()
                    if page_main['time_type'] == "the_year":
                        the_stime = yield H.getMktime("theYear")
                    elif page_main['time_type'] == "the_month":
                        the_stime = yield H.getMktime("theMonth")
                    elif page_main['time_type'] == "the_week":
                        the_stime = yield H.getMktime("theWeek")
                    elif page_main['time_type'] == "the_day":
                        the_stime = yield H.getMktime("theDay")
                    elif page_main['time_type'] == "last_month":
                        the_stime = yield H.getMktime("lastMonthOne")
                        the_etime = yield H.getMktime("lastMonth")
                    elif page_main['time_type'] == "last_year":
                        the_stime = yield H.getMktime("lastYearOne")
                        the_etime = yield H.getMktime("lastYear")
                    elif page_main['time_type'] == "recent_day":
                        the_stime = int(time.time()) - 60 * 60 * 24
                    elif page_main['time_type'] == "recent_week":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 7
                    elif page_main['time_type'] == "recent_month":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 30
                    elif page_main['time_type'] == "recent_month3":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 90
                    elif page_main['time_type'] == "recent_month6":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 180
                    elif page_main['time_type'] == "recent_year":
                        the_stime = int(time.time()) - 60 * 60 * 24 * 365
                    else:
                        the_stime = 0
                sql = "FROM trader WHERE "
                sql = sql + " trader.etime > 0 AND uaid=%s  AND trader.t_type <=1 " % page_main['uaid']
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND trader.proname like '" + search + "' "
                if the_etime != 0:
                    sql = sql + " AND trader.etime >= %s AND trader.etime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND trader.etime >= %s " % the_stime
                sql2 = "SELECT Count(*) AS t_count,Sum(trader.num) AS t_num,Sum(trader.profit) AS t_profit,Sum(trader.swap) AS t_swap," \
                      "Sum(trader.commission) AS t_comm " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                datas = cursor.fetchall()
                return datas

    # 得到历史曲线数据
    @gen.coroutine
    def getFundsCount(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                # 周
                g1 = "FROM_UNIXTIME(trader.etime,'%Y%u ')AS g_date"
                # 日
                g2 = "FROM_UNIXTIME(trader.etime,'%Y-%m-%d')AS g_date"
                # 小时
                g3 = "FROM_UNIXTIME(trader.etime,'%Y-%m-%d %H:%i')AS g_date"
                sql = "FROM trader WHERE "
                sql = sql + " (trader.etime > 0 ) AND uaid=%s AND trader.t_type <=1 " % page_main['uaid']#OR trader.t_type>=6
                sql_end = "GROUP BY g_date ORDER BY etime DESC"
                sql2 = "SELECT tid," + g2 + " " + sql + sql_end
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchone()
                if len(allnum) > 300:
                    sql3_g = g1
                elif len(allnum) < 50:
                    sql3_g = g3
                else:
                    sql3_g = g2
                sql3 = "SELECT Sum(trader.profit+trader.swap+trader.commission) AS allprofit,"
                sql3 = sql3 + sql3_g + " " + sql + sql_end
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                return datas

    # 获得持仓记录
    @gen.coroutine
    def getPositionOrderList(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                # print("search:", page_main.get('search'))
                import time
                starttime = time.time() - 7200
                sql = "FROM trader WHERE "
                sql = sql + " trader.t_type <=1 AND trader.etime = 0 AND trader.stime <= %s AND uaid=%s " % (starttime, page_main['uaid'])
                if page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    sql = sql + " AND trader.proname like '" + search + "' "
                sql2 = "SELECT COUNT(*) as allnum " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchone()
                if allnum['allnum'] > 0:
                    start = 0 if page_main.get('start') == None else page_main.get('start')
                    length = 10 if page_main.get('length') == None else page_main.get('length')
                    sql3 = "SELECT trader.orderid,trader.proname,trader.num,trader.t_type,FROM_UNIXTIME(trader.stime,'%Y-%m-%d %H:%i:%s') AS from_stime,trader.sprice,trader.etime,trader.eprice,trader.sl,trader.tp,trader.commission,trader.swap,trader.profit,trader.maxprofit,trader.minprofit " + sql + " ORDER BY orderid DESC limit %s, %s" % (int(start), int(length))
                    # print(sql3)
                    yield cursor.execute(sql3)
                    datas = cursor.fetchall()
                    if len(datas) > 0:
                        datas.append(allnum)
                        # print(datas)
                        return datas
                    else:
                        return []
                else:
                    return []

    # 得到账户持仓的手数、单量、盈利的统计
    @gen.coroutine
    def getPositionCount(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                the_stime = time.time()-7200
                sql = "FROM trader WHERE "
                sql = sql + "trader.t_type <=1 AND trader.etime = 0 AND uaid=%s " % page_main['uaid']

                sql = sql + " AND trader.stime <= %s " % the_stime
                sql2 = "SELECT Count(*) AS t_count,Sum(trader.num) AS t_num,Sum(trader.profit) AS t_profit,Sum(trader.swap) AS t_swap," \
                      "Sum(trader.commission) AS t_comm " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                datas = cursor.fetchall()
                sql3= "SELECT users_account.balance,users_account.credit,users_account.quity,users_account.profit,users_account.account,users_account.margin," \
                      "(case when (users_account.balance+users_account.credit)=0 then 0 else users_account.profit*1.00/(users_account.balance+users_account.credit)*100 end) AS profit_ratio " \
                      "FROM users_account " \
                      "WHERE uaid=%s " % page_main['uaid']
                # print(datas)
                # print(sql3)
                yield cursor.execute(sql3)
                datas2 = cursor.fetchall()
                # print(datas2)
                return datas + datas2

    # 得到账户资金的统计
    @gen.coroutine
    def getFunds(self, uaid, the_stime, the_etime):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                # the_stime = time.time()-7200
                sql = "FROM trader WHERE "
                sql = sql + " uaid=%s " % uaid
                if the_etime != 0:
                    sql = sql + " AND trader.stime >= %s AND trader.stime < %s " % (the_stime, the_etime)
                else:
                    sql = sql + " AND trader.stime >= %s " % the_stime
                sql2 = "SELECT Sum(trader.profit) AS t_in_profit " + sql + " AND trader.t_type = 6 AND trader.profit >0"
                # print(sql2)
                yield cursor.execute(sql2)
                datas = cursor.fetchone()
                sql3 = "SELECT Sum(trader.profit) AS t_in_profit " + sql + " AND trader.t_type = 6 AND trader.profit <0"
                yield cursor.execute(sql3)
                datas3 = cursor.fetchone()

                sql4 = "SELECT Sum(trader.profit) AS t_out_profit " + sql + " AND trader.t_type = 7"
                yield cursor.execute(sql4)
                datas4 = cursor.fetchone()

                sql5= "SELECT users_account.balance,users_account.credit,users_account.quity,users_account.profit,users_account.account,users_account.margin " \
                      "FROM users_account " \
                      "WHERE uaid=%s " % uaid
                # print(datas)
                # print(sql3)
                yield cursor.execute(sql5)
                datas5 = cursor.fetchone()

                if 't_in_profit' in datas3 and datas3['t_in_profit']:
                    if 't_out_profit' in datas4 and datas4['t_out_profit']:
                        datas4['t_out_profit'] = int(datas4['t_out_profit']) + int(datas3['t_in_profit']) # 999
                        datas.update(datas4)
                    else:
                        datas4['t_out_profit'] = - datas3['t_in_profit']
                        datas.update(datas4)
                datas.update(datas5)
                # print(datas)
                return datas

    # 得到账户的品种分布
    @gen.coroutine
    def getDistributedSymbol(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "FROM trader WHERE "
                sql = sql + " trader.t_type < 2 AND uaid=%s " % page_main['uaid']
                sql = "SELECT sum(trader.num) as num_all,trader.proname,trader.t_type " + sql +" GROUP BY trader.t_type,trader.proname ORDER BY trader.proname ASC,trader.t_type ASC"
                yield cursor.execute(sql)
                datas = cursor.fetchall()
                # print(datas)
                if len(datas) == 0:
                    return None, None
                else:
                    symbol_list = []
                    num_list = []
                    for data in datas:
                        if data['t_type'] == 0:
                            name_str = data['proname'] + ",buy"
                        else:
                            name_str = data['proname'] + ",sell"
                        symbol_list.append(name_str)
                        num_list.append(0 if data['num_all'] == None else data['num_all'])
                    # print(symbol_list)
                    # print(num_list)
                    return symbol_list, num_list

    # 得到盈利能力
    @gen.coroutine
    def getProfitability(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                if page_main['time_type'] == "week":
                    # 周
                    sql3_g = "FROM_UNIXTIME(trader.stime,'%Y%u ')AS g_date"
                else:
                    # 月
                    sql3_g = "FROM_UNIXTIME(trader.stime,'%Y-%m')AS g_date"
                sql = "FROM trader WHERE "
                sql = sql + " uaid=%s " % page_main['uaid']
                sql_end = "GROUP BY g_date"
                sql3 = "SELECT Sum(trader.profit+trader.swap+trader.commission) AS allprofit,"
                sql3 = sql3 + sql3_g + " " + sql + "AND trader.etime>0 AND trader.t_type <=1 " + sql_end
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                return datas