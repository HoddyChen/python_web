#coding=utf-8
#Seperate视图，分仓数组
import tornado
import json
import hashlib
import logging
# from handlers.base.base_handler import BaseHandler
from datetime import datetime
from models.user.order_model import OrderModel
from models.user.seperate_model import SeperateModel
from handlers.myredis.redis_class import RedisClass
import config
from tornado import gen

logger = logging.getLogger('Main')
class SeperateHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        get_class = self.get_argument('class')
        ukid = self.get_argument('ukid')
        AccountNumber = self.get_argument('f2')
        md5_from = self.get_argument('f5')
        Master_flag = self.get_argument('f6')
        Master_key = self.get_argument('f10')
        OrderTicket = self.get_arguments('S0')
        OrderQsid = self.get_arguments('S1')

        # 验证
        R = RedisClass()
        uaid = yield R.chick_MD5_uaid(AccountNumber, md5_from, ukid)
        followid = yield R.get_Mater_uaid(Master_key)
        followid = 0 if followid == None else followid
        logger.debug("uaid:%s" % uaid)
        if uaid > 0 and int(followid) > 0:
            #验证通过
            S = SeperateModel()
            fid = yield S.CheckFollowID(uaid, followid)
            if get_class == "set":
                yield S.delSeperateList(fid)
                order_Tuple_add = []
                for i in range(len(OrderTicket)):
                    #增加订单，元组列表
                    tupleList = (fid, int(OrderTicket[i]), int(OrderQsid[i]))
                    order_Tuple_add.append(tupleList)
                if len(order_Tuple_add) > 0:
                    # 批量增加订单
                    add_flag = yield S.AddSeperateList(order_Tuple_add)
                    if add_flag == True:
                        url_text = "1,"
                    else:
                        url_text = "-4,"
                else:
                    url_text = "0,"
            elif get_class == "get":
                # 获得缓存的分仓数组
                order_dist = yield S.getSeperateOrder(fid)
                if len(order_dist) > 0:
                    url_text = "2,"
                    for order_3 in order_dist:
                        url_text = url_text + str(order_3['orderid']) + "," + str(order_3['qsid']) + ","
                        # upnew_flag = upnew_flag + 1
                else:
                    url_text = "0,"
        else:
            # MD5不相符
            url_text = '-1,'
        logger.debug(url_text)
        self.write(url_text + config.StringEnd)
        self.finish()