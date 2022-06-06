#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import datetime
import config
from handlers.myredis.redis_class import RedisClass
import json
from models.my_socket.order_model import OrderModel
from handlers.copy_socket.socker_order_handler import SockerOrderHandler
from models.public.headers_model import global_Models

logger = logging.getLogger('Socket')
class MySocketModel(RedisClass):

    def __init__(self):
        RedisClass.__init__(self)
        self.msg_disc = {
            'uaid': 0
        }

    def __del__(self):
        RedisClass.__del__(self)
    # @gen.coroutine
    # def chick_SocketQueue(self):
    #     # 检查uaid是不是在队列 中
    #     return self.RH.sismember(config.redis_socket_queue, str(self.uaid))
    #
    # @gen.coroutine
    # def insertSocketQueue(self):
    #     # 添加单个ID到队列
    #     return self.RH.sadd(config.redis_socket_queue, str(self.uaid))
    #
    # @gen.coroutine
    # def delSocketQueue(self):
    #     # 删除队列中的元素
    #     return self.RH.srem(config.redis_socket_queue, str(self.uaid))


    #msg 解析
    def chick_msg(self, msg):
        msg = msg[:-1]
        # logger.info("[chick_user]read:%s" % msg)
        msg_disc2 = json.loads(msg)
        if type(msg_disc2).__name__ == 'dict':
            self.msg_disc.update(msg_disc2)
        return self.msg_disc

    #订单视图
    @gen.coroutine
    def chick_user(self, msg):
        try:
            self.chick_msg(msg)
            if self.chick_text():
                # logger.info("[MySocketModel:chick_user]account:%s" % self.msg_disc)
                self.msg_disc['uaid'] = yield self.chick_MD5_uaid(self.msg_disc.get('f2'), self.msg_disc.get('f5'), self.msg_disc.get('ukid'))
                # print(self.msg_disc['uaid'])
        except Exception as err:
            logger.error("[MySocketModel:chick_user]err:%s,%s" % (err, self.msg_disc['uaid']))
        finally:
            if not str(self.msg_disc['uaid']).isdigit():
                self.msg_disc['uaid'] = 0
            return self.msg_disc


    def chick_text(self):
        # 检查文本格式
        if str(self.msg_disc.get('f2')).isdigit():
            if self.msg_disc.get('f5').encode(encoding='UTF-8').isalnum():
                if self.msg_disc.get('ukid').encode(encoding='UTF-8').isalnum():
                    return True
        return False

    def chick_server_text(self):
        # 检查文本格式
        if self.msg_disc.get('key').encode(encoding='UTF-8').isalnum():
            if str(self.msg_disc.get('sendid')).isdigit():
                if self.msg_disc.get('fx_type').encode(encoding='UTF-8').isalnum():
                    if str(self.msg_disc.get('followid')).isdigit():
                        from models.public.headers_model import DistMD5
                        if DistMD5.chickDist(self.msg_disc):
                            # print("True")
                            return True
                        else:
                            # print("False")
                            return False
        return False

    @gen.coroutine
    def go_type(self):
        # 根据动作分类，执行不同的操作
        followid = 0
        if self.msg_disc['type'] == "copyorder":
            if self.msg_disc['f10'] == "" or self.msg_disc['f10'] == None or len(self.msg_disc['f10']) != 32:
                # self.RH.set(config.redis_ua_socket_end_login_time + str(self.msg_disc['uaid']), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                echotext = "5,0,0,0,0,0,0,0,0,"
            else:
                echotext, followid = yield self.get_chick_orders(self.msg_disc['uaid'])
        elif self.msg_disc['type'] == "order":
            SO = SockerOrderHandler()
            echotext = yield SO.set_orders(self.msg_disc)
        else:
            echotext = ""
        logger.debug("followid:%s" % followid)
        return echotext, int(followid)

    @gen.coroutine
    def get_chick_orders(self, uaid):
        etext = ""
        followid = None
        if uaid > 0:
            #验证通过
            followid = yield self.get_Mater_uaid(self.msg_disc['f10'])
            # followid = yield M.getMaterUaid(R, key_ma)
            logger.info("followid:%s,%s" % (followid, self.msg_disc['f10']))
            if followid:
                Mflag = yield self.chick_MaterAuthorize(followid, uaid)
                # print("Mflag:", Mflag)
                if Mflag == True:
                    etext = yield self.get_orders_sql_text(followid)
                    return etext, followid
                else:
                    etext = etext + "-2,0,0,0,0,0,0,0,0,"
            else:
                etext = etext + "-1,0,0,0,0,0,0,0,0,"
        else:
            etext = etext + "0,0,0,0,0,0,0,0,0,"
        return etext, followid

        # 前五个，用于回复重要更新，
        # self.render("user/login.html", next=self.get_argument("next"))

    @gen.coroutine
    def format_ordertext(self, order_arr):
        etext = ""
        for order in order_arr:
            # stime = time.mktime(time.strptime(order['stime'].strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S"))
            # stime = order['stime']
            logging.info(order)
            etext = etext + str(order['tid']) + "," + order['proname'] + "," + str(order['num']) + "," + str(order['t_type']) +\
                    "," + str(order['stime']) + "," + str(order['sprice']) + "," + str(order['sl']) + "," + str(order['tp']) + \
                    "," + str(order['followid']) + ","
        return etext


    @gen.coroutine
    def get_orders_text(self, master_id):
        etext = ""
        if master_id > 0:
            order_arr = yield self.get_orders_redis(master_id)
            etext2 = yield self.format_ordertext(order_arr)
            etext = etext + "1,0,0,0,0,0,0,0,0," + etext2
        else:
            etext = etext + "-1,0,0,0,0,0,0,0,0,"
        return etext

    @gen.coroutine
    def get_orders_sql_text(self, master_id, serverFMC=0):
        etext = ""
        if int(master_id) > 0:
            O = OrderModel()
            order_arr = yield O.get_PositionOrder(master_id)
            etext2 = yield self.format_ordertext(order_arr)
            logger.debug("orderNUM:%s" % len(order_arr))
            etext = etext + "1,0,0,0,0,0,0,0," + str(serverFMC) + "," + etext2
        else:
            etext = etext + "-1,0,0,0,0,0,0,0,0,"
        return etext

    # 得到策略的uaid
    @gen.coroutine
    def getMaterUaid(self, key_ma):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT uaid, fx_comment FROM master_account WHERE key_ma='%s'" % key_ma
                # print(sql)
                yield cursor.execute(sql)
                datas5 = cursor.fetchone()
                if datas5 != None:
                    return datas5['uaid'], datas5['fx_comment']
                else:
                    return None, None

    #标记各个系统间状态，0，无连接，1，接收端，2，发送端
    @gen.coroutine
    def mark_socket_global(self, label, flag, time_vol=0):
        G = global_Models()
        # R = RedisClass()
        sss_list_old = G.get("socket_server_set")
        sss_list_new = []
        sss_set_new = self.RH.smembers("socket_server_set")
        if sss_list_old == None:
            sss_list_old = []
        if len(sss_list_old) == len(sss_set_new):
            sss_list_new = yield self.set_sss_dist(label, flag, time_vol, sss_list_old)
        else:
            for sss_name in sss_set_new:
                sss = self.RH.hgetall(sss_name)
                sss_dist_new = yield self.search_sss_dist(label, flag, time_vol, sss, sss_list_old)
                if sss_dist_new == {}:
                    # 没有找到，新增
                    sss['time_vol'] = 0
                    sss['flag'] = 0  # 0,无状态；1，接收端，2，发送端
                    sss_list_new.append(sss)
                else:
                    sss_list_new.append(sss_dist_new)
        G.set_map("socket_server_set", sss_list_new)
        return

    #标记系统为接收端
    @gen.coroutine
    def set_sss_dist(self, label, flag, time_vol, sss_list_old):
        for i in range(len(sss_list_old)):
            if sss_list_old[i]['label'] == label:
                sss_list_old[i]['flag'] = flag
                if time_vol:
                    sss_list_old[i]['time_vol'] = time_vol
        return(sss_list_old)

    #搜索IP
    @gen.coroutine
    def search_sss_dist(self, label, flag, time_vol, sss, sss_list_old):
        for sss_name_old in sss_list_old:
            if sss and sss['label'] == sss_name_old['label']:
                if sss_name_old['label'] == label:
                    sss_name_old['flag'] = flag
                    if time_vol:
                        sss_name_old['time_vol'] = time_vol
                return sss_name_old
        return {}