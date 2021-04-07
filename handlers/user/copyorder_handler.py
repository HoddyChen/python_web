#coding=utf-8
#订单视图
import tornado
from tornado import gen
import hashlib
import logging
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel
import config
import time

class CopyOrderHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        get_class = self.get_argument('class')
        ukid = self.get_argument('ukid')
        AccountNumber = self.get_argument('f2')
        md5_from = self.get_argument('f5')
        # Master_flag = self.get_argument('f6')
        key_ma = self.get_argument('f10', "")
        R = RedisClass()
        uaid = yield R.chick_MD5_uaid(AccountNumber, md5_from, ukid)
        etext = ""
        if uaid > 0:
            #验证通过
            # M = MasterModel()
            followid = R.get_Mater_uaid(key_ma)
            # followid = yield M.getMaterUaid(R, key_ma)
            if followid != None:
                Mflag = yield R.chick_MaterAuthorize(followid, uaid)
                if Mflag == True:
                    order_arr = yield R.get_orders_redis(followid)
                    etext2 = yield self.format_ordertext(order_arr)
                    etext = etext + "1,0,0,0,0,0,0,0,0," + etext2
                else:
                    etext = etext + "-2,0,0,0,0,0,0,0,0,"
            else:
                etext = etext + "-1,0,0,0,0,0,0,0,0,"

        else:
            etext = etext + "0,0,0,0,0,0,0,0,0,"
        self.write(etext + config.StringEnd)
        self.finish()
        # 前五个，用于回复重要更新，
        # self.render("user/login.html", next=self.get_argument("next"))

    @gen.coroutine
    def format_ordertext(self, order_arr):
        etext = ""
        for order in order_arr:
            # stime = time.mktime(time.strptime(order['stime'].strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S"))
            # stime = order['stime']
            # print(order)
            etext = etext + str(order['tid']) + "," + order['proname'] + "," + str(order['num']) + "," + str(order['t_type']) +\
                    "," + str(order['stime']) + "," + str(order['sprice']) + "," + str(order['sl']) + "," + str(order['tp']) + \
                    "," + str(order['followid']) + ","
        return etext

