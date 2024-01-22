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
class UserModel():
    def __init__(self):
        self.R = RedisClass()

    @gen.coroutine
    def GetAccount(self, users):
        # 查交易账号存在与否，并返回有效连接MD5—KEY
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT uid,uaid,pid,account FROM usercode WHERE ptname='%s' AND account=%s AND accountserver='%s' AND vipid=1" % (users['ptname'], users['account'], users['accountserver'])
                # print(sql)
                yield cursor.execute(sql)
                datas = cursor.fetchone()
                # print(datas)
                if datas != None:
                    # 账号存在
                    # print(datas)
                    # 验证产品,生成回复
                    account_arr = yield self.GetAcountPinfo(conn, users, datas['uaid'])
                    if account_arr != None:
                        # 查询策略的参数等
                        if users['Master_flag'] == "1":
                            M = MasterModel()
                            Mater_parameter = yield M.getMaterInfo(datas['uaid'], users['pid'])
                            account_arr['max_num'] = Mater_parameter['mater_max_num']
                            account_arr['endtime'] = Mater_parameter['endtime']
                        else:
                            account_arr['max_num'] = 0
                            account_arr['endtime'] = None
                        # print(account_arr)
                        echotext = yield self.getOdata(account_arr, users['account'], datas['uaid'], users['ukid'], users['get_class'])
                    else:
                        echotext = "-9,0,0,0,0,0"
                else:
                    #账号不存在，新增账号
                    # 先验证平台与服务器
                    pt_id = yield self.GetPlatfrom(conn, users['ptname'])
                    # print(pt_id)
                    if pt_id != 0:
                        # 验证服务器
                        pfuid = yield self.GetAccountsServer(conn, users['accountserver'], pt_id)
                        if pfuid != 0:
                            # 新增交易账户users_account
                            up_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            user_url = users['accountserver'] + users['ptname']
                            try:
                                sql3 = "INSERT INTO users_account(uid,pt_id,pfuid,account,allname,balance,credit,quity," \
                                       "profit,margin,xs,ea,moni,gangan,huobi,huibimodel,stopoutlevel,stopoutmode,minlot,maxlot,user_url," \
                                       "ibpt1,adminstate,agent_time,user_update,onlinetime,start_balance) VALUES " \
                                       "(%s,%s,%s,%s,'%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s','%s',%s,%s,%s,%s,'%s',%s,%s,'%s','%s','%s',%s)"\
                                        % (1, pt_id, pfuid, users['account'], users['allname'], users['balance'],
                                          users['credit'], users['quity'], users['profit'], users['margin'],
                                          users['xs'], users['ea'], users['moni'], users['gangan'], users['huobi'],
                                          users['huibimodel'], users['stopoutlevel'], users['stopoutmode'], users['minlot'], users['maxlot'],
                                          user_url, 1, 0, up_date, up_date, up_date, users['balance'])
                                # print(sql3)
                                yield cursor.execute(sql3)
                                yield conn.commit()
                                uaid = cursor.lastrowid
                            except Exception as err:
                                yield conn.rollback()
                                logger.error("[user_model:GetAccount:INSERT]: %s" % err)
                                return None
                            # 验证产品,生成回复
                            account_arr = yield self.GetAcountPinfo(conn, users, uaid)
                            if account_arr != None:
                                echotext = yield self.getOdata(account_arr, users['account'], uaid, users['ukid'], users['get_class'])
                                if users['Master_flag'] == "1":
                                    # 加载策略到Redis
                                    O = OrderModel()
                                    # 得到账户的持仓订单
                                    datas2 = yield O.get_PositionOrder(uaid)
                                    # 进行更新redis持仓
                                    yield self.R.set_Master_order(uaid, datas2)
                                    M = MasterModel()
                                    datas3 = yield M.getMaterFollow(uaid)
                                    yield self.R.getRedisMaterFollow(datas3)
                            else:
                                echotext = "-6,0,0,0,0,0,"
                        else:
                            echotext = "-7,0,0,0,0,0,"
                    else:
                        echotext = "-8,0,0,0,0,0,"
        # print(echotext)
        # yield pool.close()
        return echotext


    @gen.coroutine
    def GetPlatfrom(self, conn, ptname):
        # 查询平台
        sql = "SELECT pt_id FROM platfrom WHERE ptname='%s'"
        with conn.cursor() as cursor:
            yield cursor.execute(sql % ptname)
            datas = cursor.fetchone()
            if datas != None:
                return datas['pt_id']
            else:
                try:
                    yield cursor.execute("INSERT INTO platfrom(ptname) VALUES('%s')" % ptname)
                    newid = conn.insert_id()
                    yield conn.commit()
                    return newid
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[user_model:GetPlatfrom:INSERT]: %s" % err)
                    return 0

    @gen.coroutine
    def GetAccountsServer(self, conn, accountserver, pt_id):
        # 查询交易服务器
        sql = "SELECT pfuid FROM plat_server WHERE accountserver='%s' and pt_id=%s"
        with conn.cursor() as cursor:
            yield cursor.execute(sql % (accountserver, pt_id))
            datas = cursor.fetchone()
            if datas != None:
                return datas['pfuid']
            else:
                try:
                    yield cursor.execute("INSERT INTO plat_server(accountserver,pt_id) VALUES('%s', %s)" % (accountserver,pt_id))
                    newid = conn.insert_id()
                    yield conn.commit()
                    return newid
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[user_model:GetAccountsServer:INSERT]: %s" % err)
                    return 0

    @gen.coroutine
    def GetAcountPinfo(self, conn, users, uaid):
        # 查询账户与产品
        up_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "SELECT acount_pinfo.pid,acount_pinfo.apflag,acount_pinfo.qq,acount_pinfo.version,acount_pinfo.pflag, acount_pinfo.probation FROM acount_pinfo WHERE pid=%s AND uaid=%s"
        with conn.cursor() as cursor:
            yield cursor.execute(sql % (users['pid'], uaid))
            datas = cursor.fetchone()
            # print("1：")
            if datas != None:
                try:
                    # 保存account_product,更新在线时间
                    # print(users['minlot'], users['maxlot'])
                    yield cursor.callproc('updata_ua_onlinedate', (uaid, users['minlot'], users['maxlot'], users['pid'], users['balance'], users['credit'], users['quity'], users['profit'], users['margin'], "@flag"))
                    yield cursor.execute("select @flag")
                    # row = cursor.fetchone()
                    # print("updata_ua_onlinedate:", row)
                except Exception as err:
                    logger.error("[user_model:GetAcountPinfo:update]: %s" % err)
                return datas
                # 预留远程参数设置
            else:
                # 新增产品到交易账号上
                # sql4 = "SELECT qq,version,probation FROM product WHERE pid=%s"
                # yield cursor.execute(sql4 % users['pid'])
                # datas2 = cursor.fetchone()
                # endtime = (datetime.datetime.now() + datetime.timedelta(days=datas2['probation'])).strftime(
                #     "%Y-%m-%d %H:%M:%S")
                sql3 = "INSERT INTO account_product(pid,uaid,apflag,starttime,onlinetime,lasttime) VALUES(%s,%s,%s,'%s','%s','%s')"
                try:
                    yield cursor.execute(sql3 % (users['pid'], uaid, 1, up_date, up_date, up_date))
                    # yield conn.commit()
                    if int(users['pid']) == 11:
                        # 新增产品订单
                        sql4 = ("INSERT INTO p_order(pid, piid, uid, uaid, otype, amount, amount_less, amount_cny, onum, otime, strattime, endtime, trade_status, potype, remarks, date_num, note) "
                                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', DATE_ADD(NOW(),INTERVAL 7 DAY), %s, %s, '%s', %s, '%s')")
                        yield cursor.execute(sql4 % (users['pid'], 6, 1, uaid, 1, 0, 0, 0, 1, up_date, up_date, 1, 1, 0, 7,'test'))
                    yield conn.commit()
                    yield cursor.execute(sql % (users['pid'], uaid))
                    datas2 = cursor.fetchone()
                    return datas2
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[user_model:GetAcountPinfo:INSERT]: %s" % err)
                    return None

    @gen.coroutine
    def getOdata(self, datas, account, uaid, ukid ,get_class):
        echotext = ""
        endtime = 0
        if datas != None:
            # 保存account_product,更新在线时间
            echotext0 = str(datas['apflag']) + ","
            # print(datas['endtime'])
            if datas.get('endtime') == None:
                endtime = 0
            else:
                endtime = time.mktime(time.strptime(datas['endtime'].strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S"))
            time_md5 = endtime - config.TineMd5Info
            echotext = echotext + str(time_md5) + ","
            # 策略参数
            if datas.get('followParameter') == None:
                datas['followParameter'] = "0"
            echotext = echotext + datas['followParameter'] + ","
            # # 开仓时间段
            # if datas['zd_opentime'] == "" or datas['zd_opentime'] == None:
            #     echotext = echotext + "0,"
            # else:
            #     echotext = echotext + datas['zd_opentime'] + ","
            # 平仓时间段
            if datas.get('zd_closetime') == "" or datas.get('zd_closetime') == None:
                echotext = echotext + "0,"
            else:
                echotext = echotext + datas.get('zd_closetime') + ","
            echotext = echotext + datas['qq'] + ","
            echotext = echotext + datas['version'] + ","
        else:
            echotext0 = "-10,0,0,0,0,0,"
        md5_time = str(int(time.time()))
        if ukid == "0":
            acount_md5 = str(account) + md5_time
            acount_md5 = hashlib.md5(acount_md5.encode(encoding='UTF-8')).hexdigest()
        else:
            acount_md5 = ukid
        self.R.RH.hset(config.redis_acount_md5_dic, acount_md5, uaid)#dic
        # print("redis_acount_md5_dic",R.RH.hget(config.redis_acount_md5_dic, acount_md5))
        self.R.RH.sadd(config.redis_uaid_set, uaid)#Set集合
        self.R.RH.set(config.redis_ua_pid_endtime + str(uaid), endtime) #到期时间
        text_md5 = str(time_md5) + str(account) + str(datas.get('pid'))
        text_md5 = hashlib.md5(text_md5.encode(encoding='UTF-8')).hexdigest()
        # 加密字符
        echotext = echotext0 + text_md5 + "," + echotext + str(acount_md5) + ","
        text_md5_2 = hashlib.md5(echotext.encode(encoding='UTF-8')).hexdigest()
        if datas.get('max_num') == None:
            datas['max_num'] = -1
        echotext = echotext + text_md5_2 + "," + md5_time + "," + str(datas.get('max_num')) + ","
        if get_class == "login":
            echotext = echotext + self.R.RH.get("server_ip") + "," + str(config.SOCKET_PORT) + ","
        # logger.info("getOdata:%s" % echotext)
        return echotext

    @gen.coroutine
    def get1data(self, datas2):
        echotext = ""
        if datas2 != None:
            echotext = echotext + str(datas2['@maxtime']) + "," + str(datas2['@maxloss']) + ","
            echotext = echotext + str(datas2['@maxnum']) + "," + str(datas2['@fixed']) + ","
            echotext = echotext + str(datas2['@percent']) + "," + str(datas2['@rate_min']) + ","
            echotext = echotext + str(datas2['@rate_max']) + "," + str(datas2['@reflex']) + ","
            echotext = echotext + str(datas2['@rate']) + "," + str(datas2['@allowed_sign']) + "," + str(datas2['@tpsl_flag']) + ","
            echotext = echotext + str(datas2['@parameter_time']) + "," + str(datas2['@pending_flag']) + "," + str(datas2['comment']) + ","
        else:
            echotext = "0,0,0,0,0,0,0,0,0,0,0,"
        # logger.info("get1data:%s" % echotext)
        return echotext

    @gen.coroutine
    def CheckAccount(self, users):
        if self.R.RH.hexists(config.redis_acount_md5_dic, users['ukid']):
            datas = {}
            uaid = self.R.RH.hget(config.redis_acount_md5_dic, users['ukid'])
            datas2 = yield self.updataAccount(users, uaid)
            # pp = redis_ua_pid_endtime + str(uaid)
            # print(R.RH.get(redis_ua_pid_endtime + str(uaid)))
            # endtime = int(float(R.RH.get(config.redis_ua_pid_endtime + str(uaid))))
            M = MasterModel()
            if users['Master_flag'] != "1":
                # 非策略账号
                master_id = yield self.R.get_Mater_uaid(users['MasterKey'])
                comment = yield self.R.get_Mater_Comment(users['MasterKey'])
                if master_id == None:
                    return "-11,0,0,0,0,0,"
                # follow_parameter = yield R.getMaterParameter(master_id, users['pid'])
                follow_parameter = yield M.getMaterInfo(master_id, users['pid'])
                # 加入策略参数
                datas['followParameter'] = str(int(follow_parameter['position_maxnum'])) + "." + follow_parameter['spsl'] + "." + follow_parameter['reverse'] + "."
                datas['endtime'] = follow_parameter['endtime']
                datas2['comment'] = comment
            else:
                Mater_parameter = yield M.getMaterInfo(uaid, users['pid'])
                datas['max_num'] = Mater_parameter['mater_max_num']
                datas['endtime'] = Mater_parameter['endtime']
                datas2['comment'] = "fx"

            # datas['endtime'] = datetime.datetime.fromtimestamp(endtime)
            datas['pid'] = users['pid']
            datas['apflag'] = 1
            datas['zd_opentime'] = ""
            datas['zd_closetime'] = ""
            datas['qq'] = self.R.RH.get(config.redis_qq_pid + str(users['pid']))
            datas['version'] = self.R.RH.get(config.redis_version_pid + str(users['pid']))
            echotext = yield self.getOdata(datas, users['account'], uaid, users['ukid'], users['get_class'])
            echotext2 = yield self.get1data(datas2)
            # logger.info("CheckAccount:" + echotext + echotext2)
            return echotext + echotext2
        else:
            # 账户未登陆或已经失效
            return "-12,0,0,0,0,0,"

    @gen.coroutine
    def getProdctOrderInfo(self, uaid, pid):
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
                yield cursor.execute(sql, (uaid, pid))
                datas = cursor.fetchall()
                MaterInfo = {}
                MaterInfo['endtime'] = None# 到期时间
                if len(datas) > 0:
                    # print(datas)
                    for data in datas:
                        if data['strattime'] <= datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'):
                            if MaterInfo['endtime'] == None:
                                MaterInfo['endtime'] = data['endtime']
                            else:
                                if data['endtime'] > MaterInfo['endtime']:
                                    MaterInfo['endtime'] = data['endtime']

        logger.debug("MaterInfo%s" % MaterInfo)
        return MaterInfo


    @gen.coroutine
    def CheckAccountSb(self, users):
        if self.R.RH.hexists(config.redis_acount_md5_dic, users['ukid']):
            datas={}
            uaid = self.R.RH.hget(config.redis_acount_md5_dic, users['ukid'])
            # datas2 = yield self.updataAccount(users, uaid)
            # pp = redis_ua_pid_endtime + str(uaid)
            # print(R.RH.get(redis_ua_pid_endtime + str(uaid)))
            # endtime = int(float(R.RH.get(config.redis_ua_pid_endtime + str(uaid))))

            # follow_parameter = yield R.getMaterParameter(master_id, users['pid'])
            follow_parameter = yield self.getProdctOrderInfo(uaid, users['pid'])
            # 加入策略参数
            datas['endtime'] = follow_parameter['endtime']

            # datas['endtime'] = datetime.datetime.fromtimestamp(endtime)
            datas['pid'] = users['pid']
            datas['apflag'] = 1
            datas['zd_opentime'] = ""
            datas['zd_closetime'] = ""
            datas['qq'] = self.R.RH.get(config.redis_qq_pid + str(users['pid']))
            datas['version'] = self.R.RH.get(config.redis_version_pid + str(users['pid']))
            echotext = yield self.getOdata(datas, users['account'], uaid, users['ukid'], users['get_class'])
            # echotext2 = yield self.get1data(datas2)
            # logger.info("CheckAccount:" + echotext + echotext2)
            return echotext
        else:
            # 账户未登陆或已经失效
            return "-12,0,0,0,0,0,"

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
                                           float(users['profit']), float(users['margin']), int(users['tpsl_flag']), int(users['pending_flag']),
                                           "@maxtime", "@maxloss","@maxnum", "@fixed", "@percent", "@rate_min", "@rate_max", "@reflex",
                                           "@rate", "@allowed_sign", "@parameter_time", "@tpsl_flag", "@flag", "@pending_flag"))
                    yield cursor.execute("SELECT @maxtime,@maxloss,@maxnum,@fixed,@percent,@rate_min,@rate_max,@reflex,@rate,@allowed_sign,@parameter_time,@tpsl_flag,@flag,@pending_flag")
                    row = cursor.fetchone()
                    # print("AA:", row)
                except Exception as err:
                    row = None
                    logger.error("[user_model:updataAccount:update]: %s" % err)
        return row


