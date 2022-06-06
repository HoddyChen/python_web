#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import config
import datetime
import time
import hashlib
from handlers.myredis.redis_class import RedisClass
from models.public.headers_model import Headers_Models
import pandas as pd
import json

class StrategyModel():
    logger = logging.getLogger('Main')
    time_period = [20, 30, 60, 120, 200, 250, 360]

    @gen.coroutine
    def getStraegyInfoList(self, page_main):
        # 返回查询策略列表
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                # print("search:", page_main.get('search'))
                if page_main == None or page_main.get('search') == "0" or page_main.get('search') == "":
                    sql = "FROM predict_info  WHERE `pi_status` = 1 "
                else:
                    search = "%" + page_main.get('search') + "%"
                    sql = "FROM predict_info WHERE `pi_status`=1 & `strategy_name` like '%s' AND " % search

                sql2 = "SELECT COUNT(*) as allnum " + sql
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchone()
                if allnum['allnum'] > 0:
                    start = 0 if page_main.get('start') == None else page_main.get('start')
                    length = 10 if page_main.get('length') == None else page_main.get('length')
                    sql3 = "SELECT strategy_id, strategy_name, uaid, last_time, pi_status " + sql + " ORDER BY strategy_id DESC limit %s, %s" % (int(start), int(length))
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
    def getStrategyLoging(self, page_main=None):
        copyStrategy_list = yield self.getStraegyInfoList(page_main)
        if len(copyStrategy_list) <= 0:
            return []
        else:
            copy_list = []
            now_time = int(time.time())
            for i in range(len(copyStrategy_list)-1):
                copy_dist = {}
                if copyStrategy_list[i]['last_time'] != None or copyStrategy_list[i]['last_time'] != "null":
                    try:
                        if time.mktime(copyStrategy_list[i]['last_time'].timetuple()) + 1200 < now_time:
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

    @gen.coroutine
    def getStrategyCount(self, page_main=None):
        # 返回统计数据
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                if page_main == None:
                    return []
                H = Headers_Models()
                the_year = yield H.getMktime("theYear")
                the_month = yield H.getMktime("theMonth")
                the_week = yield H.getMktime("theWeek")

                # 持仓统计
                sql = "SELECT Sum(trader.num) as out_position_num,Sum(trader.swap) as out_position_swap,Sum(trader.commission) as out_position_comm,Sum(trader.profit) as out_position_profit,COUNT(*) as out_position_order_num FROM trader WHERE t_type < 2 AND uaid = " + str(page_main['uaid']) + " AND etime = 0"
                yield cursor.execute(sql)
                data = cursor.fetchone()
                # 今天
                sql2 = "SELECT Sum(trader.swap) as out_swap_today,Sum(trader.commission) as out_comm_today,Sum(trader.profit) as out_profit_today FROM trader WHERE t_type < 2 AND uaid = " + str(page_main['uaid']) + " AND etime > unix_timestamp(curdate())"
                yield cursor.execute(sql2)
                data2 = cursor.fetchone()
                # 当周
                sql3 = "SELECT Sum(trader.swap) as out_swap_week,Sum(trader.commission) as out_comm_week,Sum(trader.profit) as out_profit_week FROM trader WHERE t_type < 2 AND uaid = " + str(page_main['uaid']) + " AND etime > " + str(the_week)
                yield cursor.execute(sql3)
                data3 = cursor.fetchone()
                # 当月
                sql4 = "SELECT Sum(trader.swap) as out_swap_month,Sum(trader.commission) as out_comm_month,Sum(trader.profit) as out_profit_month FROM trader WHERE t_type < 2 AND uaid = " + str(page_main['uaid']) + " AND etime > " + str(the_month)
                yield cursor.execute(sql4)
                data4 = cursor.fetchone()
                # 当年
                sql5 = "SELECT Sum(trader.swap) as out_swap_year,Sum(trader.commission) as out_comm_year,Sum(trader.profit) as out_profit_year FROM trader WHERE t_type < 2 AND uaid = " + str(page_main['uaid']) + " AND etime > " + str(the_year)
                yield cursor.execute(sql5)
                data5 = cursor.fetchone()
                # 全部
                sql6 = "SELECT Sum(trader.swap) as out_swap_all,Sum(trader.commission) as out_comm_all,Sum(trader.profit) as out_profit_all FROM trader WHERE t_type < 2 AND uaid = " + str(page_main['uaid']) + " AND etime > 0"
                yield cursor.execute(sql6)
                data6 = cursor.fetchone()
                # 统计资金
                sql7 = "SELECT balance as out_balance, credit as out_credit, quity as out_quity, profit as out_profit FROM users_account WHERE uaid = " + str(page_main['uaid'])
                yield cursor.execute(sql7)
                data7 = cursor.fetchone()
                # 格式化
                data = yield self.getDictValue(data)
                data2 = yield self.getDictValue(data2)
                data3 = yield self.getDictValue(data3)
                data4 = yield self.getDictValue(data4)
                data5 = yield self.getDictValue(data5)
                data6 = yield self.getDictValue(data6)
                # 计算
                try:
                    data7['out_position_profit'] = data['out_position_swap'] + data['out_position_comm'] + data['out_position_profit']
                    data7['out_today'] = data2['out_swap_today'] + data2['out_comm_today'] + data2['out_profit_today']
                    data7['out_week'] = data3['out_swap_week'] + data3['out_comm_week'] + data3['out_profit_week']
                    data7['out_month'] = data4['out_swap_month'] + data4['out_comm_month'] + data4['out_profit_month']
                    data7['out_year'] = data5['out_swap_year'] + data5['out_comm_year'] + data5['out_profit_year']
                    data7['out_all'] = data6['out_swap_all'] + data6['out_comm_all'] + data6['out_profit_all']
                    data7['out_position_num'] = data['out_position_num']
                    data7['out_position_order_num'] = data['out_position_order_num']
                except:
                    data7['out_position_profit'] = 0
                    data7['out_today'] = 0
                    data7['out_week'] = 0
                    data7['out_month'] = 0
                    data7['out_year'] = 0
                    data7['out_all'] = 0
                    data7['out_position_num'] = 0
                    data7['out_position_order_num'] = 0
        return data7

    # 得到策略的持仓品种分布(只分品种，不分方向)
    @gen.coroutine
    def getDictValue(self, data_):
        for key in data_.keys():
            if data_[key] == None:
                data_[key] = 0
        return data_

    # 得到策略的持仓品种分布(只分品种，不分方向)
    @gen.coroutine
    def getStrategySymbol(self, page_main=None, etime_flag=True):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                if etime_flag == True:
                    etime_str = ">"
                else:
                    etime_str = "<="
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT sum(trader.num) as num_all,trader.proname,trader.t_type FROM trader WHERE trader.etime " + etime_str + " 0 AND trader.t_type < 2 AND trader.uaid = %s GROUP BY trader.proname ORDER BY trader.proname ASC,trader.t_type ASC"
                yield cursor.execute(sql, (page_main['uaid'],))
                datas = cursor.fetchall()
                # print(datas)
                if len(datas) == 0:
                    return None, None
                else:
                    symbol_list = []
                    num_list = []
                    for data in datas:
                        symbol_list.append(data['proname'])
                        num_list.append(0 if data['num_all'] == None else data['num_all'])
                    # print(symbol_list)
                    # print(num_list)
                    return symbol_list, num_list

    # 得到策略的持仓品种分布(分品种，分方向)
    @gen.coroutine
    def getStrategySymbol2(self, page_main=None, etime_flag=True):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                if etime_flag == True:
                    etime_str = ">"
                else:
                    etime_str = "<="
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT sum(trader.num) as num_all,trader.proname,trader.t_type FROM trader WHERE trader.etime " + etime_str + " 0 AND trader.t_type < 2 AND trader.uaid = %s GROUP BY trader.t_type,trader.proname ORDER BY trader.proname ASC,trader.t_type ASC"
                yield cursor.execute(sql, (page_main['uaid'],))
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

    # 得到策略的持仓品种列表(分品种，分方向)
    @gen.coroutine
    def getStrategySymbolList(self, page_main=None):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql =  "FROM trader WHERE trader.etime <= 0 AND trader.t_type < 2 AND trader.uaid = %s GROUP BY trader.t_type,trader.proname " % page_main['uaid']
                sql2 = "SELECT trader.proname " + sql
                yield cursor.execute(sql2)
                datas2 = cursor.fetchall()

                start = 0 if page_main.get('start') == None else page_main.get('start')
                length = 12 if page_main.get('length') == None else page_main.get('length')
                sql3 = "SELECT count(*) as t_all, sum(trader.num) as num_all, trader.proname, trader.t_type, sum(commission) as commission_all,sum(swap) as swap_all, sum(profit) as profit_all " + sql + " ORDER BY proname ASC,t_type ASC,num_all ASC limit %s, %s" % (int(start), int(length))
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": len(datas2)})
                    # print(datas)
                    return datas
                else:
                    return []


    # 得到历史曲线数据
    @gen.coroutine
    def getFundsCount(self, page_main=None):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # print(page_main.get('time_type'))
                # 周
                g1 = "DATE_FORMAT(FROM_UNIXTIME(trader.etime),'%Y%u ') AS g_date"
                # 日
                g2 = "DATE_FORMAT(FROM_UNIXTIME(trader.etime),'%Y-%m-%d') AS g_date"
                # 小时FROM_UNIXTIME(etime)
                g3 = "DATE_FORMAT(FROM_UNIXTIME(trader.etime),'%Y-%m-%d %H') AS g_date"
                sql = "FROM trader WHERE "
                sql = sql + " (trader.etime > 0 ) AND uaid=%s " % page_main['uaid']#OR trader.t_type>=6
                sql_end = " GROUP BY g_date"
                sql_end2 = " ORDER BY etime DESC"
                sql2 = "SELECT tid, " + g2 + " " + sql + sql_end
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchall()
                if len(allnum) > 300:
                    sql3_g = g1
                elif len(allnum) < 50:
                    sql3_g = g3
                else:
                    sql3_g = g2
                sql3 = "SELECT Sum(profit+swap+commission) AS allprofit,"
                sql3 = sql3 + sql3_g + " " + sql + sql_end + sql_end2
                # print(sql3)
                yield cursor.execute(sql3)
                datas = cursor.fetchall()
                return datas

    # 得到策略的持仓品种
    @gen.coroutine
    def getStrategySymbolName(self, page_main=None):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT symbol_name, ma_v, open_flag, portfolio_weight FROM predict_stratepy WHERE strategy_id = %s ORDER BY symbol_name ASC"
                yield cursor.execute(sql, (page_main['strategy_id'],))
                datas = cursor.fetchall()
                # print(datas)
                if len(datas) == 0:
                    return []
                else:
                    return datas

    # 得到策略的MA线图
    @gen.coroutine
    def getStrategySymbolMa(self, page_main=None):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT predict_date AS g_date, straregy_cumsum FROM predict WHERE strategy_id = %s AND symbol_name = %s ORDER BY predict_date DESC  limit 800"
                yield cursor.execute(sql, (page_main['strategy_id'], page_main['symbol_name']))
                datas = cursor.fetchall()
                # print(datas)
                if len(datas) > 0:
                    datas = pd.DataFrame(list(reversed(datas)))
                    for timeperiod_ in self.time_period:
                        datas['sg_ma' + str(timeperiod_)] = datas['straregy_cumsum'].rolling(timeperiod_).mean()
                    datas['g_date'] = datas['g_date'].apply(lambda x: str(x.strftime('%Y-%m-%d %H')))
                    datas_columns = list(datas.columns)
                    datas_columns.remove("g_date")
                    return json.loads(datas.to_json(orient='records')), datas_columns
                else:
                    return [], []

    # 得到策略的MA的的设置
    @gen.coroutine
    def getStrategySymbolMaPeriod(self, page_main=None):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT ma_v, open_flag FROM predict_stratepy WHERE strategy_id = %s AND symbol_name = %s"
                yield cursor.execute(sql, (page_main['strategy_id'], page_main['symbol_name']))
                datas = cursor.fetchone()
                # print(datas)
                if len(datas) > 0:
                    return datas
                else:
                    return {}

    # 策略的MA的的设置
    @gen.coroutine
    def setStrategyPeriod(self, page_main=None):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "update predict_stratepy SET ma_v = %s WHERE strategy_id = %s AND symbol_name = %s"
                    yield cursor.execute(sql, (int(page_main['time_type']), int(page_main['strategy_id']), page_main['symbol_name']))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    self.logger.error("[StrategyModel:setStrategyPeriod] %s" % err)
                    return False

    # 策略的货币开关设置
    @gen.coroutine
    def setStrategyOpenFlag(self, page_main=None):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    if int(page_main['fx_flag']) == 0:
                        page_main['fx_flag'] = 1
                    else:
                        page_main['fx_flag'] = 0
                    sql = "update predict_stratepy SET open_flag = %s WHERE strategy_id = %s AND symbol_name = %s"
                    yield cursor.execute(sql, (
                    int(page_main['fx_flag']), int(page_main['strategy_id']), page_main['symbol_name']))
                    yield conn.commit()
                    if page_main['fx_flag'] == 1:
                        return 1
                    else:
                        return 0
                except Exception as err:
                    yield conn.rollback()
                    self.logger.error("[StrategyModel:setStrategyOpenFlag] %s" % err)
                    return 9


    # 策略的订单统计
    @gen.coroutine
    def getOrderCount(self, page_main=None):
        if page_main == None:
            return []
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    if page_main == None:
                        the_etime = 0
                    else:
                        from models.public.headers_model import Headers_Models
                        H = Headers_Models()
                        if page_main['time_type'] == "the_year":
                            the_stime = yield H.getMktime("theYear")
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m') as group_time "
                        elif page_main['time_type'] == "the_month":
                            the_stime = yield H.getMktime("theMonth")
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m%d') as group_time "
                        elif page_main['time_type'] == "the_week":
                            the_stime = yield H.getMktime("theWeek")
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m%d') as group_time "
                        elif page_main['time_type'] == "last_month":
                            the_stime = yield H.getMktime("lastMonthOne")
                            the_etime = yield H.getMktime("lastMonth")
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m%d') as group_time "
                        elif page_main['time_type'] == "last_year":
                            the_stime = yield H.getMktime("lastYearOne")
                            the_etime = yield H.getMktime("lastYear")
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m') as group_time "
                        elif page_main['time_type'] == "recent_week":
                            the_stime = int(time.time()) - 60 * 60 * 24 * 7
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m%d') as group_time "
                        elif page_main['time_type'] == "recent_month":
                            the_stime = int(time.time()) - 60 * 60 * 24 * 30
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m%d') as group_time "
                        elif page_main['time_type'] == "recent_month3":
                            the_stime = int(time.time()) - 60 * 60 * 24 * 90
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m%d') as group_time "
                        elif page_main['time_type'] == "recent_month6":
                            the_stime = int(time.time()) - 60 * 60 * 24 * 180
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m%d') as group_time "
                        elif page_main['time_type'] == "recent_year":
                            the_stime = int(time.time()) - 60 * 60 * 24 * 365
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m') as group_time "
                        else:
                            the_stime = 0
                            select_sql = " DATE_FORMAT(FROM_UNIXTIME(etime), '%Y%m') as group_time "
                    sql = "FROM trader WHERE uaid = %s AND etime > 0 " % page_main['uaid']

                    if page_main['time_type'].find("last") >= 0:
                        sql = sql + " AND etime >= %s AND etime < %s " % (the_stime, the_etime)
                    else:
                        sql = sql + " AND etime >= %s " % the_stime
                    sql2 = "SELECT uaid, " + select_sql + sql + " GROUP BY group_time "
                    # print(sql2)
                    yield cursor.execute(sql2)
                    datas2 = cursor.fetchall()
                    start = 0 if page_main.get('start') == None else page_main.get('start')
                    length = 10 if page_main.get('length') == None else page_main.get('length')
                    sql3 = "SELECT " + select_sql + ", Count(*) AS t_count,Sum(trader.num) AS t_num,Sum(trader.profit) AS t_profit,Sum(trader.swap) AS t_swap," \
                           "Sum(trader.commission) AS t_comm "
                    sql3 = sql3 + sql + " GROUP BY group_time ORDER BY group_time DESC limit %s, %s" % (int(start), int(length))
                    # print(sql3)
                    yield cursor.execute(sql3)
                    datas = cursor.fetchall()
                    if len(datas) > 0:
                        datas.append({"allnum": len(datas2)})
                        return datas
                    else:
                        return []
                except Exception as err:
                    yield conn.rollback()
                    self.logger.error("[StrategyModel:getOrderCount] %s" % err)
                    return []