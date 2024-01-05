#coding=utf-8
#订单视图
import tornado
import logging
from models.my_socket.order_model import OrderModel
from tornado import gen

logger = logging.getLogger('Socket')
class SockerOrderHandler():

    # def __init__(self):
    #     # RedisClass.__init__(self)
    #     pass

    @gen.coroutine
    def set_orders(self, msg_disc):
        try:
            O = OrderModel()
            url_text = "2,"
            upnew_flag = 0
            #把OrderTicket转成元组
            TicketTuple = yield O.FormatTuple(msg_disc['orderlist'])
            Order_datas = yield O.CheckOrderList(msg_disc['uaid'], TicketTuple)
            order_Tuple_add = []
            order_Tuple_edit = []
            for order in msg_disc['orderlist']:
                edit_flag = 0
                for Order_data in Order_datas:
                    if order['H1'] == str(Order_data['orderid']):
                        #存在订单
                        if order['H5'] != str(Order_data['etime']):
                            edit_flag = 1
                        if order['H6'] != str(Order_data['t_type']):
                            edit_flag = 1
                        if order['H7'] != str(Order_data['num']):
                            edit_flag = 1
                        if order['H8'] != str(Order_data['sl']):
                            edit_flag = 1
                        if order['H9'] != str(Order_data['tp']):
                            edit_flag = 1
                        if edit_flag == 1:
                            # 修改订单，元组列表
                            tupleList2 = (order['H0'], float(order['H7']), int(order['H6']), int(order['H3']),
                                          float(order['H2']), int(order['H5']), float(order['H4']),
                                          float(order['H8']), float(order['H9']), float(order['HB']),
                                          float(order['HC']), float(order['HG']), float(order['HE']),
                                          float(order['HF']), order['HA'], int(order['HD']),
                                          msg_disc['uaid'], int(order['H1']))
                            order_Tuple_edit.append(tupleList2)
                        else:
                            #无须修改的
                            url_text = url_text + order['H1'] + ",1,"
                        edit_flag = 2
                        break

                if edit_flag == 0:
                    #增加订单，元组列表
                    if "from" in order['HA']:
                        follow_id = yield O.findFollowid(order['HA'], msg_disc['uaid'])
                        if follow_id == None:
                            follow_id = order['HJ']
                    else:
                        follow_id = order['HJ']
                    tupleList = (msg_disc['uaid'], int(order['H1']), order['H0'], float(order['H7']), int(order['H6']),
                                 int(order['H3']), float(order['H2']), int(order['H5']), float(order['H4']),
                                 float(order['H8']), float(order['H9']), float(order['HB']), float(order['HC']),
                                 float(order['HG']), float(order['HE']), float(order['HF']), order['HA'],
                                 int(order['HD']), int(follow_id))
                    order_Tuple_add.append(tupleList)
            if len(order_Tuple_add) > 0:
                # 批量增加订单
                add_flag = yield O.AddOrderList(order_Tuple_add)
                if add_flag == True:
                    orderid_new_list = []
                    add_edit_flag = 0
                    for order_1 in order_Tuple_add:
                        url_text = url_text + str(order_1[1]) + ",1,"
                        # print("=add_edit_flag=%s" % type(order_1[18]))
                        if order_1[18] == "0" or order_1[18] == 0:
                            # print(order_1[1])
                            orderid_new_list.append(str(order_1[1]))
                            add_edit_flag = 1
                        upnew_flag = upnew_flag + 1
                    #修改跟单ID
                    # print("edit_tuple=%s" % edit_tuple)
                    if add_edit_flag == 1:
                        # print("add_edit_flag：orderid_str=%s" % orderid_new_list)
                        O.UpOrderFollowID(tuple(orderid_new_list), msg_disc['uaid'])
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
            # if upnew_flag > 0 and msg_disc['f6'] == "1" and self.RH.sismember(config.redis_master_uaid_set, msg_disc['uaid']):
            #     C = CommcandModel()
            #     yield C.setMarginCommcand(0, int(msg_disc['uaid']), "MakeOpenOrder")

            #     # 得到账户的持仓订单
            #     datas = yield O.get_PositionOrder(msg_disc['uaid'])
            #     # 进行更新redis持仓
            #     yield self.set_Master_order(msg_disc['uaid'], datas)
            #     # 加入socket队列
            #     yield self.insertMaterAuthorizeSocketQueue(str(msg_disc['uaid']))

            return url_text
        except Exception as e:
            logger.error("[SockerOrderHandler,set_orders]%s" % e)
            for order_2 in order_Tuple_add:
                url_text = url_text + str(order_2[1]) + ",0,"
            for order_4 in order_Tuple_edit:
                url_text = url_text + str(order_4[17]) + ",0,"
            return url_text
