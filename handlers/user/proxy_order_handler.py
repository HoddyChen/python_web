#coding=utf-8
#代理订单视图
import tornado
import json
import hashlib
import logging
# from handlers.base.base_handler import BaseHandler
from datetime import datetime
from models.user.proxy_order_model import ProxyOrderModel
from handlers.myredis.redis_class import RedisClass
import config
from tornado import gen

logger = logging.getLogger('Main')
class ProxyOrderHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        #self.render("user/login.html", next=self.get_argument("next"))
        get_class = self.get_argument('class')
        ukid = self.get_argument('ukid')
        AccountNumber = self.get_argument('f2')
        md5_from = self.get_argument('f5')
        Master_flag = self.get_argument('f6')
        OrderTicket = self.get_arguments('H0')
        OpenT = self.get_arguments('H1')
        OrderComment = self.get_arguments('H2')
        # print(type(OrderComment))
        # for ii in OrderComment:
        #     print(ii)
        account = self.get_arguments('H3')
        OrderProfit = self.get_arguments('H4')
        proxy_from_orderid = self.get_arguments('H5')
        # 验证
        R = RedisClass()
        uaid = yield R.chick_MD5_uaid(AccountNumber, md5_from, ukid)
        # print("uaid:", uaid)
        if uaid > 0:
            #验证通过
            O = ProxyOrderModel()
            url_text = "2,"
            upnew_flag = 0
            #把OrderTicket转成元组
            TicketTuple = yield O.FormatTuple(OrderTicket)
            accountTuple = yield O.FormatTuple(account)
            Order_datas = yield O.CheckOrderList(uaid, TicketTuple)
            order_Tuple_add = []
            order_Tuple_edit = []
            GradePrice = yield O.findProxyGradePrice(accountTuple)
            # print(GradePrice)
            for i in range(len(OrderTicket)):
                edit_flag = 0
                for Order_data in Order_datas:
                    if str(OrderTicket[i]) == str(Order_data['orderid']):
                        #存在订单
                        if OpenT[i] != str(Order_data['stime']):
                            edit_flag = 1
                        if account[i] != str(Order_data['account']):
                            edit_flag = 1
                        if OrderProfit[i] != str(Order_data['profit']):
                            edit_flag = 1
                        if proxy_from_orderid[i] != str(Order_data['proxy_from_orderid']):
                            edit_flag = 1

                        # print(OrderComment[i])
                        # print(Order_data['comment'])
                        if OrderComment[i] != str(Order_data['comment']):
                            edit_flag = 1
                        if Order_data['proxy_profit']:
                            if Order_data['proxy_profit'] > 0 or str(Order_data['proxy_profit']) != "0.000":
                                edit_flag = 2
                        if edit_flag == 1:
                            # 修改订单，元组列表
                            tupleList2 = (int(OpenT[i]), int(proxy_from_orderid[i]), OrderComment[i], int(account[i]),
                                          float(OrderProfit[i]), float(OrderProfit[i]) / config.PROXY_PRICE * GradePrice[i], 1, uaid, int(OrderTicket[i]))
                            order_Tuple_edit.append(tupleList2)
                        else:
                            #无须修改的
                            url_text = url_text + OrderTicket[i] + ",1,"
                        edit_flag = 2
                        break

                if edit_flag == 0:
                    #增加订单，元组列表
                    tupleList = (int(OrderTicket[i]), int(proxy_from_orderid[i]), int(account[i]), int(OpenT[i]),
                                 float(OrderProfit[i]), float(OrderProfit[i]) / config.PROXY_PRICE * GradePrice[i], OrderComment[i], uaid, 1)
                    order_Tuple_add.append(tupleList)
            if len(order_Tuple_add) > 0:
                # 批量增加订单
                add_flag = yield O.AddOrderList(order_Tuple_add)
                if add_flag == True:
                    orderid_str = ""
                    add_edit_flag = 0
                    for order_1 in order_Tuple_add:
                        url_text = url_text + str(order_1[0]) + ",1,"
                        # print("==%s" % type(order_1[18]))
                else:
                    for order_2 in order_Tuple_add:
                        url_text = url_text + str(order_2[0]) + ",0,"
            if len(order_Tuple_edit) > 0:
                    # 修改订单
                    up_flag = yield O.UpOrderList(order_Tuple_edit)
                    if up_flag == True:
                        for order_3 in order_Tuple_edit:
                            url_text = url_text + str(order_3[8]) + ",1,"
                            upnew_flag = upnew_flag + 1
                    else:
                        for order_4 in order_Tuple_edit:
                            url_text = url_text + str(order_4[8]) + ",0,"

        else:
            if uaid == -1:
                # MD5不相符
                url_text = '-1,-1,0,0,0,0,0,0,0,'
            else:
                #不存在或是没有登陆
                url_text = '-1,-2,0,0,0,0,0,0,0,'
        # print(url_text)
        self.write(url_text + config.StringEnd)
        self.finish()
        # #整理数据
        # if users['ea'] =="true" or users['ea'] == 1:
        #     users['ea'] == 1
        # else:
        #     users['ea'] == 0
        # if users['moni'] == "true":
        #     users['moni'] == 1
        # else:
        #     users['moni'] == 0
        # #
        # md5_str = users['account'] + users['version']
        # str_md5 = hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()
        # # 验证
        # #datas = ""
        # y = UserModel()
        # if users['md5_from'] == str_md5:
        #     if get_class == "check":
        #         datas = yield y.GetAccount(users)#tornado.gen.Task
        #       # 执行Task函数，内部还是返回future对象。Task函数上第一个参数是要执行的函数，第二个是参数
        #
        #         self.write(datas)
        # else:
        #     self.write('-1,0,0,0,0,0,0,0,0,')
        # self.finish()
    #登录成功附加别的属性
    # def success_login(self, user):
    #     user.last_login = datetime.now()
    #     user.loginnum += 1
    #     self.db.add(user)
    #     self.db.commit()
    #     self.session.set('username', user.user_name)