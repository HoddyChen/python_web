#coding=utf-8
#订单视图
import tornado
import json
import hashlib
import logging
# from handlers.base.base_handler import BaseHandler
from datetime import datetime
from models.user.order_model import OrderModel
from handlers.myredis.redis_class import RedisClass
import config
from tornado import gen

logger = logging.getLogger('Main')
class OrderHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        #self.render("user/login.html", next=self.get_argument("next"))
        get_class = self.get_argument('class')
        ukid = self.get_argument('ukid')
        AccountNumber = self.get_argument('f2')
        md5_from = self.get_argument('f5')
        Master_flag = self.get_argument('f6')
        OrderSymbol = self.get_arguments('H0')
        OrderTicket = self.get_arguments('H1')
        OrderOpenPrice = self.get_arguments('H2')
        OpenT = self.get_arguments('H3')
        OrderClosePrice = self.get_arguments('H4')
        CloseT = self.get_arguments('H5')
        OrderType = self.get_arguments('H6')
        OrderLots = self.get_arguments('H7')
        OrderStopLoss = self.get_arguments('H8')
        OrderTakeProfit = self.get_arguments('H9')
        OComment = self.get_arguments('HA')
        OrderCommission = self.get_arguments('HB')
        OrderSwap = self.get_arguments('HC')
        OrderMagicNumber = self.get_arguments('HD')
        MaxProfit = self.get_arguments('HE')
        MinProfit = self.get_arguments('HF')
        OrderProfit = self.get_arguments('HG')
        followid = self.get_arguments('HJ')
        # 验证
        R = RedisClass()
        uaid = yield R.chick_MD5_uaid(AccountNumber, md5_from, ukid)
        # print("uaid:", uaid)
        if uaid > 0:
            #验证通过
            O = OrderModel()
            url_text = "2,"
            upnew_flag = 0
            #把OrderTicket转成元组
            TicketTuple = yield O.FormatTuple(OrderTicket)
            Order_datas = yield O.CheckOrderList(uaid, TicketTuple)
            order_Tuple_add = []
            order_Tuple_edit = []
            for i in range(len(OrderSymbol)):
                edit_flag = 0
                for Order_data in Order_datas:
                    if OrderTicket[i] == str(Order_data['orderid']):
                        #存在订单
                        if CloseT[i] != str(Order_data['etime']):
                            edit_flag = 1
                        if OrderStopLoss[i] != str(Order_data['sl']):
                            edit_flag = 1
                        if OrderTakeProfit[i] != str(Order_data['tp']):
                            edit_flag = 1
                        if  edit_flag == 1:
                            # 修改订单，元组列表
                            tupleList2 = (OrderSymbol[i], float(OrderLots[i]), int(OrderType[i]),int(OpenT[i]),
                                          float(OrderOpenPrice[i]), int(CloseT[i]), float(OrderClosePrice[i]),
                                          float(OrderStopLoss[i]), float(OrderTakeProfit[i]), float(OrderCommission[i]),
                                          float(OrderSwap[i]),float(OrderProfit[i]), float(MaxProfit[i]),
                                          float(MinProfit[i]), OComment[i], int(OrderMagicNumber[i]),
                                          uaid, int(OrderTicket[i]))
                            order_Tuple_edit.append(tupleList2)
                        else:
                            #无须修改的
                            url_text = url_text + OrderTicket[i] + ",1,"
                        edit_flag = 2
                        break

                if edit_flag == 0:
                    #增加订单，元组列表
                    if "from" in OComment[i]:
                        follow_id = yield O.findFollowid(OComment[i], uaid)
                    else:
                        follow_id = followid[i]
                    tupleList = (uaid, int(OrderTicket[i]), OrderSymbol[i], float(OrderLots[i]), int(OrderType[i]),
                                 int(OpenT[i]), float(OrderOpenPrice[i]), int(CloseT[i]), float(OrderClosePrice[i]),
                                 float(OrderStopLoss[i]), float(OrderTakeProfit[i]), float(OrderCommission[i]), float(OrderSwap[i]),
                                 float(OrderProfit[i]), float(MaxProfit[i]), float(MinProfit[i]), OComment[i],
                                 int(OrderMagicNumber[i]), int(follow_id))
                    order_Tuple_add.append(tupleList)
            if len(order_Tuple_add) > 0:
                # 批量增加订单
                add_flag = yield O.AddOrderList(order_Tuple_add)
                if add_flag == True:
                    orderid_str = ""
                    add_edit_flag = 0
                    for order_1 in order_Tuple_add:
                        url_text = url_text + str(order_1[1]) + ",1,"
                        # print("==%s" % type(order_1[18]))
                        if order_1[18] == "0" or order_1[18] == 0:
                            # print(order_1[1])
                            orderid_str = orderid_str + str(order_1[1]) + ","
                            add_edit_flag = 1
                        upnew_flag = upnew_flag + 1
                    #修改跟单ID
                    # print("edit_tuple=%s" % edit_tuple)
                    if add_edit_flag == 1:
                        # print("orderid_str=%s" % orderid_str)
                        O.UpOrderFollowID(orderid_str[0:-1], uaid)
                else:
                    for order_2 in order_Tuple_add:
                        url_text = url_text + str(order_2[1]) + ",0,"
            if len(order_Tuple_edit) > 0:
                    # 修改订单
                    up_flag = yield O.UpOrderList(order_Tuple_edit)
                    if up_flag == True:
                        for order_3 in order_Tuple_edit:
                            url_text = url_text + str(order_3[17]) + ",1,"
                            upnew_flag = upnew_flag + 1
                    else:
                        for order_4 in order_Tuple_edit:
                            url_text = url_text + str(order_4[17]) + ",0,"
            # 判断是不是主策略账户
            if upnew_flag > 0 and Master_flag == "1" and R.RH.sismember(config.redis_master_uaid_set, uaid):
                # 得到账户的持仓订单
                datas = yield O.get_PositionOrder(uaid)
                # 进行更新redis持仓
                yield R.set_Master_order(uaid, datas)
                # 加入socket队列
                yield R.insertMaterAuthorizeSocketQueue(str(uaid))
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