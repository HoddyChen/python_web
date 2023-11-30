#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import hashlib
import datetime
import config
from handlers.myredis.redis_class import RedisClass
import json

logger = logging.getLogger('Main')
class MasterModel():

    # 得到跟单用户的列表
    @gen.coroutine
    def getMaterFollow(self, followid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT uaid,follow_flag,followid,f_flag,account,allname,last_time FROM follow_view WHERE followid=%s" % followid
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchall()
        return datas

    # 检查跟单用户与策略的关系
    @gen.coroutine
    def checkMaterAndFollow(self, followid, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                if followid is None:
                    followid = 0
                sql = "SELECT uaid,follow_flag,followid,f_flag FROM follow WHERE followid = %s AND uaid = %s"
                # print(sql % (followid, uaid))
                yield cursor.execute(sql % (followid, uaid))
                datas = cursor.fetchone()
        return datas


    # 检查跟单用户是否存在，不存在则增加，返回
    @gen.coroutine
    def checkMaterFollow(self, followid, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT uaid,follow_flag,followid,f_flag FROM follow WHERE followid = %s AND uaid = %s"
                # logger.info(sql)
                yield cursor.execute(sql % (followid, uaid))
                datas = cursor.fetchone()
                if datas == None:
                    try:
                        up_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        sql2 = "INSERT INTO follow(uaid,follow_flag,followid,f_flag,update_time) VALUES(%s, %s, %s, %s,'%s')" % (uaid, 0, followid, 1, up_date)
                        # logger.info(sql2)
                        yield cursor.execute(sql2)
                        yield conn.commit()
                    except Exception as err:
                        yield conn.rollback()
                        logger.error("[master_model:checkMaterFollow:INSERT]: %s" % err)
                        return False
        return True

    # 得到策略的uaid
    @gen.coroutine
    def getMaterUaid(self, key_ma):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT uaid FROM master_account WHERE key_ma='%s'" % key_ma
                # print(sql)
                yield cursor.execute(sql)
                datas5 = cursor.fetchone()
                if datas5 != None:
                    return datas5['uaid']
                else:
                    return None


    @gen.coroutine
    def getVcmial(self, umail, uaid):
        up_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    # R = RedisClass()
                    sql6 = "SELECT key_ma FROM master_account WHERE uaid=%s"
                    yield cursor.execute(sql6 % (uaid))
                    datas6 = cursor.fetchone()
                    # 查询用户
                    sql = "SELECT uid,email FROM ua_user WHERE uaid=%s"
                    yield cursor.execute(sql % (uaid))
                    datas = cursor.fetchone()
                    if datas6 != None:
                        # yield R.insert_master_uaid(datas6['key_ma'], uaid)
                        # 验证邮箱与uaid的匹配
                        if datas.get('email') == umail:
                            return datas6['key_ma']
                        else:
                            return None
                    else:
                        # 未注册的策略账户
                        #判断是不是VIPID
                        sql2 = "SELECT uid,vipid FROM vip"
                        # sql6 = "update account_product set lasttime = '%s'  WHERE uaid=%s"
                        yield cursor.execute(sql2)
                        datas2 = cursor.fetchall()
                        uid_flag = 0
                        vipid = 1
                        for vip_uid in datas2:
                            if vip_uid['uid'] == datas['uid']:
                                uid_flag = 1
                                vipid = vip_uid['vipid']
                                break
                        key_text = umail + up_date
                        key_ma = hashlib.md5(key_text.encode(encoding='UTF-8')).hexdigest()
                        # print("uid_flag:", uid_flag)
                        # print(uid_flag,",", config.PID,",", 64,",", vipid,",", uaid,",", umail,",", datas.get('email'),",", key_ma,",","@out_mflag")
                        yield cursor.callproc('insert_master',
                                              (uid_flag, config.PID, 64, vipid, uaid, umail, datas.get('email'), key_ma,"@out_mflag"))
                        yield cursor.execute("select @out_mflag;")
                        row = cursor.fetchone()
                        logger.debug("insert_master:", row)
                        if row == None:
                            return None
                        else:
                            # logger.info("insert_master:", row)
                            if row['@out_mflag'] == 1:
                                # yield conn.commit()
                                return key_ma
                            else:
                                logger.error("insert_master:", row)
                                return None
                            # if uid_flag == 1:
                        #     #未独立user账号,则独立建立
                        #     # 查询是不是已经存在email用户
                        #     sql7 = "SELECT uid,email FROM users WHERE email='%s'"
                        #     yield cursor.execute(sql7 % (umail))
                        #     datas7 = cursor.fetchone()
                        #     if datas7 == None:
                        #         sql3 = "INSERT INTO users(email,emailflag,vipid,starttime,flag) VALUES('%s', %s, %s, '%s', %s)"
                        #         yield cursor.execute(sql3 % (umail, 1, vipid, up_date, 1))
                        #         uid = conn.insert_id()
                        #     else:
                        #         uid = datas7["uid"]
                        #     sql4 = "update users_account set uid = %s WHERE uaid = %s"
                        #     yield cursor.execute(sql4 % (uid, uaid))
                        #     sql5 = "INSERT INTO master_account(key_ma, uaid, flag_ma) VALUES('%s', %s, %s)"
                        #     yield cursor.execute(sql5 % (key_ma, uaid, 1))
                        #     yield conn.commit()
                        # else:
                        #     #已经有user账号
                        #     # 验证邮箱与uaid的匹配
                        #     if datas.get('email') == umail:
                        #         sql5 = "INSERT INTO master_account(key_ma, uaid, flag_ma) VALUES('%s', %s, %s)"
                        #         yield cursor.execute(sql5 % (key_ma, uaid, 1))
                        #         yield conn.commit()
                        #     else:
                        #         return None
                except Exception as err:
                    # yield conn.rollback()
                    logger.error("[master_model:getVcmial:update or INSERT]: %s" % err)
                    return None

    # 获得策略方的邮箱
    @gen.coroutine
    def getMasterEmail(self, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    # 查询用户
                    sql = "SELECT uid,email FROM ua_user WHERE uaid=%s"
                    yield cursor.execute(sql % (uaid))
                    datas = cursor.fetchone()
                    if datas != None:
                        return datas
                except Exception as err:
                    logger.error("[master_model:getVcmial:update or INSERT]: %s" % err)
        return None

    # 更新策略的授权
    @gen.coroutine
    def setMaterAuthorize(self, followid, uaid, follow_flag):
        if uaid != None and followid != None:
            with (yield pool.Connection()) as conn:
                with conn.cursor() as cursor:
                    sql = "update follow set follow_flag = %s WHERE followid = %s AND uaid=%s" % (follow_flag, followid, uaid)
                    # print(sql)
                    try:
                        yield cursor.execute(sql)
                        yield conn.commit()
                        return True
                    except Exception as err:
                        yield conn.rollback()
                        logger.error("[master_model:setMaterAuthorize:update]: %s" % err)
                        return False
        else:
            return False

    # 获得跟单账户的有效总数
    @gen.coroutine
    def get_copy_num(self, master_uaid_Hash):
        num = 0
        for i in master_uaid_Hash:
            if master_uaid_Hash[i] == "1" or master_uaid_Hash[i] == 1:
                num = num + 1
        return num

    # 得到购买的跟单账号数量
    @gen.coroutine
    def getMaterCopyNum(self, pid, masterid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT SUM(p_order.onum) AS maxnum FROM p_order WHERE p_order.uaid = %s AND p_order.pid = %s " \
                      "AND p_order.strattime < now() AND p_order.endtime > now() AND p_order.otype = 1"
                # print(sql)
                yield cursor.execute(sql, (masterid, pid))
                datas = cursor.fetchone()
                # print(int(datas['maxnum']))
                if datas['maxnum'] == None:
                    return 0
                else:
                    return int(datas['maxnum'])

    # 得到购买的策略账号资料///架构修改，已不用
    # @gen.coroutine
    # def getMaterCopyInfo(self, masterid, pid):
    #     with (yield pool.Connection()) as conn:
    #         with conn.cursor() as cursor:
    #             # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
    #             sql = "SELECT * FROM account_product WHERE pid=%s AND uaid=%s"
    #             # print(sql)
    #             yield cursor.execute(sql, (pid, masterid))
    #             datas = cursor.fetchone()
    #     return datas

    # 得到购买的策略账号资料,时间，订单及方案的参数
    @gen.coroutine
    def getMaterInfo(self, masterid, pid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT product_info.piname,product.pname_cn,product.pname_en,p_order.oid,p_order.uaid," \
                      "p_order.otype,p_order.amount,p_order.amount_less,p_order.amount_cny,p_order.onum,p_order.strattime, " \
                      "p_order.trade_status,p_order.endtime,product_info.info10,product_info.info11,product_info.info12 " \
                      "FROM p_order " \
                      "INNER JOIN product_info ON p_order.piid = product_info.piid " \
                      "INNER JOIN product ON product_info.pid = product.pid " \
                      "WHERE p_order.uaid = %s AND product_info.pid = %s AND p_order.endtime > now() AND p_order.otype = 1"
                # logger.debug(sql % (masterid, pid))
                yield cursor.execute(sql, (masterid, pid))
                datas = cursor.fetchall()
                MaterInfo = {}
                MaterInfo['mater_max_num'] = 0# 可用跟单账户数量
                MaterInfo['endtime'] = None# 到期时间
                MaterInfo['position_maxnum'] = 0# info10持仓最大限制
                MaterInfo['spsl'] = "0"# info11止损止盈
                MaterInfo['reverse'] = "0"# info11反向平仓
                if len(datas) > 0:
                    # print(datas)
                    for data in datas:
                        if data['strattime'] <= datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'):
                            MaterInfo['mater_max_num'] = MaterInfo['mater_max_num'] + data['onum']
                            if MaterInfo['endtime'] == None:
                                MaterInfo['endtime'] = data['endtime']
                            else:
                                if data['endtime'] > MaterInfo['endtime']:
                                    MaterInfo['endtime'] = data['endtime']
                            if int(data['info10']) > MaterInfo['position_maxnum']:
                                MaterInfo['position_maxnum'] = int(data['info10'])
                            #info11止损止盈
                            if data['info11'] == "1":
                                MaterInfo['spsl'] = "1"
                            #info11反向平仓
                            if data['info12'] == "1":
                                MaterInfo['reverse'] = "1"
        logger.debug("MaterInfo%s" % MaterInfo)
        return MaterInfo

    # 得到跟单账号统计数量
    @gen.coroutine
    def getMaterCopyCount(self, masterid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT Count(*) as follow_num, follow.follow_flag FROM follow WHERE follow.followid = %s " \
                      "GROUP BY follow.follow_flag ORDER BY follow.follow_flag ASC"
                # print(sql % masterid)
                yield cursor.execute(sql, (masterid,))
                datas = cursor.fetchall()
        return datas

    # web 策略账号登陆
    @gen.coroutine
    def checkMaterMail(self, email):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT * FROM master_users WHERE email=%s"
                # print(sql)
                yield cursor.execute(sql, email)
                datas = cursor.fetchall()
        return datas

    # 获得策略方的KEY
    @gen.coroutine
    def getMasterKEY(self, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    # 查询用户
                    sql = "SELECT * FROM ma_parameter WHERE uaid=%s"
                    yield cursor.execute(sql % (uaid))
                    datas = cursor.fetchone()
                    if datas != None:
                        return datas
                except Exception as err:
                    logger.error("[master_model:getVcmial:update or INSERT]: %s" % err)
        return None

    # 获得策略方的在线时间
    @gen.coroutine
    def getMasterTime(self, uaid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    # 查询用户
                    sql = "SELECT uaid, account, allname, onlinetime as last_time FROM users_account WHERE uaid=%s"
                    yield cursor.execute(sql % (uaid))
                    datas = cursor.fetchone()
                    if datas != None:
                        return datas
                except Exception as err:
                    logger.error("[master_model:getMasterTime]: %s" % err)
        return None