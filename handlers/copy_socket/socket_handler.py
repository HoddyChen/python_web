# coding=utf-8
from tornado.tcpserver import TCPServer
from tornado import ioloop, gen, iostream
from models.my_socket.my_socket_model import MySocketModel
from models.public.headers_model import DistMD5
from handlers.client_socket.client_handler import SocketClientModel
import logging
import config
import time
import json
from handlers.myredis.redis_class import RedisClass
from models.public.headers_model import global_Models

logger = logging.getLogger('Socket')
class Connection(object):
    clients = set()
    clients_sss = set()
    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self.clients_state = True
        # self.client_list = client_list
        self.msg_disc = {
            'uaid': -1,
            'followid': -1,
            'sendid': -1,
            'return': -1,
            'time_vol': 0,
        }
        self.S = None
        self.G = global_Models()
        self._stream.set_close_callback(self.on_close)
        self.read_message()

    @gen.coroutine
    def read_message(self):
        try:
            if self._stream.closed() == True:
                logger.debug("closeed:%s" % self._stream.closed())
                return
            msg = yield self._stream.read_until(bytes("\n", encoding="utf8"))
            if msg != "":
                # logger.debug(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                logger.debug("all_link:%s,read-msg:%s" % (len(Connection.clients), msg))
                self.msg_disc['time_vol'] = time.time()
                self.S = MySocketModel()
                msg_str = bytes.decode(msg)
                if msg_str.find(config.ServerMd5Info) >= 0:
                    # 总服务器命令
                    chick_disc = self.S.chick_msg(msg)
                    self.msg_disc.update(chick_disc)
                    # flag = yield S.chick_server_text()
                    if self.S.chick_server_text():
                        # yield self.server_messages()
                        # 把client 转到clients_sss
                        # yield S.mark_socket_global(self.msg_disc.get('label'), 1, int(time.time()))
                        if self in Connection.clients_sss:
                            pass
                        else:
                            if self in Connection.clients:
                                Connection.clients_sss.add(self)
                                Connection.clients.remove(self)

                        self.G.set_map("ServerTime", int(time.time()))
                        yield self.server_process()
                    else:
                        logger.error("[Connection:Server]no...uaid")
                        yield self.on_close()
                else:
                    # 验证用户
                    chick_disc = yield self.S.chick_user(msg)
                    self.msg_disc.update(chick_disc)
                    logger.info(self.msg_disc)
                    if self.msg_disc.get('uaid') > 0 and self.msg_disc.get('uaid') != None:
                        echo_msg, followid = yield self.S.go_type()
                        if followid >= 0:
                            self.msg_disc['followid'] = followid
                        yield self.broadcast_messages(echo_msg)
                    else:
                        # 不存在或是没有登陆
                        # echo_msg = '-1,-2,0,0,0,0,0,0,0,'
                        logger.error("[Connection:read_message]no...uaid")
                        yield self.on_close()
            else:
                logger.error("[Connection:read_message]msg,None...")
                yield self.on_close()
        except Exception as e:
            logger.error("[Connection:read_message]uaid:%s, error:%s" % (self.msg_disc.get('uaid'), e))
            # yield self.remove_clients_state()

    @gen.coroutine
    def close_same_label(self):
        try:
            None_conn_list = []
            for clients_conn in Connection.clients_sss:
                # print("chick_conn:%s" % conn.socket_uaid)
                if clients_conn.msg_disc.get('label') == None or clients_conn.msg_disc.get('label') == "":
                    None_conn_list.append(clients_conn)
                    continue
                if clients_conn.msg_disc.get('label') == self.msg_disc.get('label'):
                    if clients_conn._address != self._address:
                        # Connection.clients.remove(clients_conn)
                        None_conn_list.append(clients_conn)
                        # yield self.on_close_Manual(clients_conn)
            if len(None_conn_list) > 0:
                # logger.debug("[Connection:close_same_label]None_conn.close_strat....")
                for clients_conn in None_conn_list:
                    yield self.on_close_Manual(clients_conn)
                    # logger.info("[Connection:close_same_uaid]%s,%s" % (clients_conn.msg_disc['uaid'], clients_conn._address))
            return
        except Exception as e:
            logger.error("[Connection:close_same_label]error:%s" % e)
        return

    @gen.coroutine
    def close_same_uaid(self):
        try:
            None_conn_list = []
            for clients_conn in Connection.clients:
                # print("chick_conn:%s" % conn.socket_uaid)
                if clients_conn.msg_disc.get('uaid') < 0 or clients_conn.msg_disc.get('followid') < 0:
                    None_conn_list.append(clients_conn)
                    continue
                if clients_conn.msg_disc.get('uaid') == self.msg_disc.get('uaid') and clients_conn.msg_disc.get('followid') == self.msg_disc.get('followid'):
                    if clients_conn._address != self._address:
                        # Connection.clients.remove(clients_conn)
                        None_conn_list.append(clients_conn)
                        # yield self.on_close_Manual(clients_conn)
            if len(None_conn_list) > 0:
                # logger.debug("[Connection:close_same_uaid]None_conn.close_strat....")
                for clients_conn in None_conn_list:
                    yield self.on_close_Manual(clients_conn)
                        # logger.info("[Connection:close_same_uaid]%s,%s" % (clients_conn.msg_disc['uaid'], clients_conn._address))
            return
        except Exception as e:
            logger.error("[Connection:close_same_uaid]error:%s" % e)
        return

    # 总系统请求处理,新
    @gen.coroutine
    def server_process(self):
        try:
            # G = global_Models()
            msgDist = self.msg_disc.copy()
            msgDist['label'] = self.G.get("label")
            if msgDist['fx_type'] == "MakeUpOrder":
                # 发送补仓命令
                flag_num = yield self.TraversingConnection(msgDist.get('sendid'), msgDist.get('followid'))
                msgDist['return'] = flag_num
                msgDist['fx_type'] = "ReturnStatus"
                msgDist['key'] = DistMD5.encryptDist(msgDist)
                logger.debug("MakeUpOrder:%s" % flag_num)
                yield self.send_message(json.dumps(msgDist), msgDist.get('sendid'))
            elif msgDist['fx_type'] == "MakeOpenOrder":
                # 发送开仓命令
                flag_num = yield self.TraversingConnection(msgDist.get('sendid'), msgDist.get('followid'))
                msgDist['return'] = flag_num
                msgDist['fx_type'] = "ReturnStatus"
                msgDist['key'] = DistMD5.encryptDist(msgDist)
                # logger.debug("MakeOpenOrder:%s" % flag_num)
                yield self.send_message(json.dumps(msgDist), msgDist.get('followid'))
            elif msgDist['fx_type'] == "ChickStatus":
                msgDist['return'] = 5
                msgDist['fx_type'] = "ReturnStatus"
                msgDist['key'] = DistMD5.encryptDist(msgDist)
                yield self.send_message(json.dumps(msgDist), msgDist.get('label'))
                # 保持与其他服务器的连接
                # time.sleep(60)
                # yield self.socket_between_process(0, 0)
            elif msgDist['fx_type'] == "ReturnStatus":

                logger.info("ReturnStatus:followid:%s" % msgDist.get('followid'))
            else:
                # 无命令
                logger.debug("[no-process]%s" % msgDist)
                # yield self.on_close()
                # return
            # logger.debug("send_end:%s" % self.msg_disc)
            self.G.set_map("ServerTime", int(time.time()))
            # yield self.close_same_label()
            if self.S:
                # print("del S...")
                self.S = None
            yield self.read_message()
        except Exception as e:  # iostream.StreamClosedError
            logger.error("[Connection:server_process]error:%s" % e)

    #系统间交换数据, 组织数据
    @gen.coroutine
    def socket_between_process(self, sendid, followid, fx_type=None):
        msgDist = {}
        msgDist["sendid"] = int(sendid)
        msgDist["followid"] = int(followid)
        msgDist["fx_type"] = fx_type
        if msgDist["fx_type"] == None:
            msgDist["fx_type"] = "MakeOpenOrder"
        # G = global_Models()
        msgDist['label'] = self.G.get("label")
        msgDist['key2'] = config.ServerMd5Info
        msgDist['key'] = DistMD5.encryptDist(msgDist)
        yield self.socket_server_process(msgDist)
        # G.set_map("ServerTime", int(time.time()))
        # yield self.socket_client_process(msgDist)

    #系统间交换数据, 作为发送端
    # @gen.coroutine
    # def socket_client_process(self, msgDist):
    #     SC = SocketClientModel()
    #     yield SC.ClientHandshake(msgDist)

    #系统间交换数据, 作为接收端
    @gen.coroutine
    def socket_server_process(self, msgDist):
        # 处理待发送数据
        msg_str = json.dumps(msgDist)
        for server_conn in Connection.clients_sss:
            if str(server_conn.msg_disc.get('label')) == "999":
                continue
            yield server_conn.send_message(msg_str, msgDist["followid"])
            logger.debug("[server_process_msg]%s" % msg_str)
        self.G.set_map("ServerTime", int(time.time()))
        return

    # # 总系统请求处理
    # @gen.coroutine
    # def server_messages(self):
    #     try:
    #         import json
    #         if self.msg_disc['fx_type'] == "MakeUpOrder":
    #             # 发送补仓命令
    #             flag_num = yield self.TraversingConnection(self.msg_disc.get('sendid'), self.msg_disc.get('followid'))
    #             self.msg_disc['return'] = flag_num
    #             self.msg_disc['key'] = DistMD5.encryptDist(self.msg_disc)
    #             logger.debug("MakeUpOrder:%s" % flag_num)
    #             yield self.send_message(json.dumps(self.msg_disc), self.msg_disc.get('sendid'))
    #         elif self.msg_disc['fx_type'] == "MakeOpenOrder":
    #             # 发送开仓命令
    #             flag_num = yield self.TraversingConnection(self.msg_disc.get('sendid'), self.msg_disc.get('followid'))
    #             self.msg_disc['return'] = flag_num
    #             self.msg_disc['key'] = DistMD5.encryptDist(self.msg_disc)
    #             # logger.debug("MakeOpenOrder:%s" % flag_num)
    #             yield self.send_message(json.dumps(self.msg_disc), self.msg_disc.get('followid'))
    #         else:
    #             # 无命令
    #             yield self.on_close()
    #         logger.debug("send_end:%s" % self.msg_disc)
    #         yield self.read_message()
    #     except Exception as e:  # iostream.StreamClosedError
    #         logger.error("[Connection:server_messages]error:%s" % e)

    # 用户请求处理
    @gen.coroutine
    def broadcast_messages(self, data):
        try:
            if self.msg_disc.get('type') == "copyorder":
                yield self.send_message(data, self.msg_disc.get('uaid'))
                logger.debug("[chick_me]%s,[followid]%s,[copyorder-send-data]%s" % (self.msg_disc.get('uaid'), self.msg_disc.get('followid'), data))
                # 保持与其他服务器的连接
                # yield self.socket_between_process(0, 0, "ChickStatus")
            elif self.msg_disc.get('type') == "order":
                yield self.socket_between_process(0, self.msg_disc.get('uaid'), "MakeOpenOrder")
                # 发布
                yield self.TraversingConnection(0, self.msg_disc.get('uaid'))
                yield self.send_message(data, self.msg_disc.get('uaid'))
                logger.debug("[order-send][uaid]%s, [data]%s" % (self.msg_disc.get('uaid'), data))
            else:
                yield self.send_message("", None)
                logger.debug("type no")
            self.msg_disc['time_vol_send_A'] = time.time() - self.msg_disc['time_vol']
            logger.debug("send_A,run_time:%s S" % self.msg_disc['time_vol_send_A'])
            # 判断进行与总部的连接
            ServerTime = self.G.get("ServerTime")
            if int(time.time()) - ServerTime > 3 * 55:
                yield self.socket_between_process(0, 0, "ChickStatus")
            if self.msg_disc.get('uaid') != None:
                if self.msg_disc.get('uaid') > 0:
                    yield self.close_same_uaid()
                    yield self.read_message()
                else:
                    # print("uaid《0")
                    logger.error("[Connection:broadcast_messages]uaid<=0")
                    yield self.on_close()
            else:
                # print("None")
                logger.error("[Connection:broadcast_messages]uaid为空")
                yield self.on_close()
                # yield self.read_message()

            # seG = global_Models()

        except Exception as e:#iostream.StreamClosedError
            logger.error("[Connection:broadcast_messages]error:%s" % e)

    @gen.coroutine
    def TraversingConnection(self, sendid, followid):
        # 发布指定策略信号
        # logger.debug("TraversingConnection")
        try:
            # S = MySocketModel()
            flag_num = 0
            endtime = self.S.RH.get(config.redis_ua_pid_endtime + str(followid))
            if endtime:
                # followid存在
                if int(float(endtime)) - time.time() > 0:
                    # 在有效期内
                    if self.msg_disc.get('fx_type') == "MakeUpOrder":#int(sendid) > 0 or
                        data2 = yield self.S.get_orders_sql_text(followid, 1)
                    else:
                        data2 = yield self.S.get_orders_sql_text(followid, 0)
                    # logger.debug("send_B:%s" % data2)
                    # logger.debug("send_B,time:%s" % time.time())
                    self.msg_disc['time_vol_send_B'] = time.time() - self.msg_disc['time_vol']
                    logger.debug("send_B,run_time:%s S" % self.msg_disc['time_vol_send_B'])
                    for clients_conn in Connection.clients:
                        # print("chick_conn:%s" % clients_conn.msg_disc.get('uaid'))
                        if clients_conn.msg_disc.get('uaid') != None:
                            if clients_conn.msg_disc.get('uaid') > 0 and clients_conn.msg_disc.get('uaid') != followid and clients_conn.msg_disc.get('followid') == followid:
                                flag = yield self.S.chick_MaterAuthorize(followid, clients_conn.msg_disc.get('uaid'))
                                if flag and (sendid == 0 or sendid == clients_conn.msg_disc.get('uaid')):
                                    # logger.info("[Connection:TraversingConnection]chick_conn_OK:%s,%s" % (clients_conn.msg_disc['uaid'], clients_conn._address))
                                    yield clients_conn.send_message(data2, clients_conn.msg_disc.get('uaid'))
                                    flag_num += 1
                                # else:
                                #     logger.error("chick_conn_UaidNoAuthorize:%s" % (clients_conn._address,))
                        else:
                            logger.debug("[Connection:TraversingConnection]chick_conn_NO2:%s" % (clients_conn._address,))
                    if flag_num > 0:
                        logger.debug("[send_data]%s" % data2)
                else:
                    logger.debug("[Connection:TraversingConnection] Expired")
                # self.msg_disc['time_vol_send_end'] = time.time() - self.msg_disc['time_vol']
            else:
                flag_num = 0
            self.S = None
            return flag_num
        except Exception as e:
            logger.error("[Connection:TraversingConnection] Expired", e)
            return flag_num


    @gen.coroutine
    def send_message(self, data, uaid):
        try:
            logger.debug("[sendTo]{uaid}:%s, {IP}:%s" % (uaid, self._address))#
            if not self._stream.closed():
                yield self._stream.write(bytes(data + config.StringEnd + "\n", encoding="utf8"))
            else:
                logger.error("[Connection:send_message]error:_stream已经失效{uaid}:%s, {IP}:%s, {data}:%s" % (uaid, self._stream._address, data))
            return
        except Exception as e:
            logger.error("[Connection:send_message]error:%s, {uaid}:%s, {IP}:%s, {data}:%s" % (e, uaid, self._stream._address, data))

    @gen.coroutine
    def on_close(self):
        try:
            logger.debug("[Connection:on_close]A user out: %s" % (self._address,))
            # print("close:%s" % (not self._stream.closed()))
            # print(Connection.clients(self))#
            # Connection.clients.close(self)
            # Connection.clients.
            if not self._stream.closed():
                yield self._stream.close()
            yield self.remove_clients_state()
            # yield self.remove_clients_state()

            # self.clients.remove()
            # Connection.clients.remove(self)
            # Remove this reference to self, which would otherwise cause a
            # yield self._clear_request_state()
        except Exception as e:
            logger.error("[Connection:on_close]error:%s" % e)
        finally:
            return

    @gen.coroutine
    def on_close_Manual(self, clients_conn):
        try:
            logger.debug("[on_close_Manual]A user out: %s" % (clients_conn._address,))
            # print("close:%s" % (not self._stream.closed()))
            if not clients_conn._stream.closed():
                clients_conn._stream.close()
            yield self.remove_clients_state(clients_conn)
        except Exception as e:
            logger.error("[Connection:on_close_Manual]error:%s" % e)
        finally:
            return

    @gen.coroutine
    def remove_clients_state(self, clients_conn=None):
        """remove clients标志.
        """
        # logger.info("remove_clients_state")
        try:
            if clients_conn == None:
                # if self.clients_state == True:
                if self in Connection.clients:
                    Connection.clients.remove(self)
                elif self in Connection.clients_sss:
                    Connection.clients_sss.remove(self)
                self.clients_state = False
                logger.debug("[remove_clients_state:self]remove:%s" % (self._address,))
            else:
                if clients_conn in Connection.clients:
                    Connection.clients.remove(clients_conn)
                    logger.debug("[remove_clients_state:clients_conn]remove:%s" % (clients_conn._address,))
                elif clients_conn in Connection.clients_sss:
                    Connection.clients_sss.remove(clients_conn)
                    logger.debug("[remove_clients_state:clients_conn_sss]remove:%s" % (clients_conn._address,))
                clients_conn.clients_state = False
                logger.debug("[remove_clients_state:clients_conn]remove:%s" % (clients_conn._address,))
        except Exception as e:
            logger.error("[Connection:remove_clients_state]error:%s" % e)
        finally:
            return


class CopyServer(TCPServer):
    # 可尝试SSL参数时使用
    # def __init__(self):
    #     print(self)
    #     # super(CopyServer, self).__init__(*args, **kwargs)
    #     self.client_id = args[0]
    #     self.devices = dict()
    #     import time
    #     time.sleep(10)
    #     from start_client_test import chick_redisConsole
    #
    #     chick_redisConsole()

    @gen.coroutine
    def handle_stream(self, stream, address):
        # stream.socket.settimeout(10)
        from tornado.iostream import StreamClosedError

        try:
            # yield self.initClientIP(stream.socket.getsockname())
            logger.debug("New connection :%s" % (address,))
            C = Connection(stream, address)
            # SocketClientModel(self.client_id)
            # c1.sock_while()
            logger.debug("connection servernum is:%s" % len(C.clients))
            logger.debug("connection client num is:%s" % len(C.clients_sss))
            # while True:
            #     try:
            #
            #         yield C.get_SocketQueue()
            #     except Exception as e:
            #         # logger.error("[CopyServer]:%s" % e)
            #         yield C.on_close()
            #         break
            # data = yield stream.read_until(b"\n")
            # yield stream.write(data)

        except Exception as err:
        # except StreamClosedError:
            logger.error("[CopyServer:handle_stream]%s" % err)
            # return

    @gen.coroutine
    def initClientIP(self, sockname):
        # 获得需要通知的服务器列表
        R = RedisClass()
        G = global_Models()
        sss_list_new = []
        sss_list_old = G.get("socket_server_set")
        if sss_list_old == None:
            sss_list_old = []
        for sss_name in R.RH.smembers("socket_server_set"):
            sss = R.RH.hgetall(sss_name)
            flag = 0
            for sss_name_old in sss_list_old:
                if sss['host'] == sss_name_old['host'] and int(sss['port']) == int(sss_name_old['port']):
                    flag = 1
                    sss_list_new.append(sss_name_old)
            if flag == 0:
            # 不存在则增加
                if sss and (sss['host'], int(sss['port'])) != sockname:
                # 不是自身服务器
                    sss['time_vol'] = 0
                    sss['flag'] = 0  # 0,无状态；1，接收端，2，发送端
                    sss['me'] = 0  # 0,其他服务器；1，自己本身
                else:
                    sss['time_vol'] = 0
                    sss['flag'] = 0  # 0,无状态；1，接收端，2，发送端
                    sss['me'] = 1  # 0,其他服务器；1，自己本身
                sss_list_new.append(sss)
        G.set_map("socket_server_set", sss_list_new)
        return