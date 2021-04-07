# coding=utf-8
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from tornado import ioloop, gen, iostream
from models.my_socket.my_socket_model import MySocketModel
import logging
import config
import time

logger = logging.getLogger('Socket')
class Connection(object):
    clients = set()

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self.clients_state = True
        self.msg_disc = {
            'uaid': 0,
        }
        self._stream.set_close_callback(self.on_close)
        # self.S = MySocketModel()
        self.read_message()
        # logger.info("----------------")
        # logger.info("A new user entered.%s" % str(address))

    @gen.coroutine
    def read_message(self):
        try:
            if self._stream.closed() == True:
                # print("closeed:%s" % self._stream.closed())
                return
            # if time.time() > 1571036720:
            #     yield self.on_close()
            msg = yield self._stream.read_until(bytes("\n", encoding="utf8"))
            # print("msg:%s" % msg)
            if msg != "":
                # print("-1-%s" % self.msg_disc.get('uaid'))
                logger.info("all_link:%s,msg:%s" % (len(Connection.clients), msg))
                # 验证用户
                S = MySocketModel()
                # print("-2-%s" % self.msg_disc.get('uaid'))
                self.msg_disc = yield S.chick_user(msg)
                # print("-3-%s" % self.msg_disc.get('uaid'))
                # logger.info("uaid:%s" % self.msg_disc['uaid'])
                if self.msg_disc.get('uaid') > 0 and self.msg_disc.get('uaid') != None:
                    # if self.msg_disc.get('type') == "copyorder":
                    yield self.close_same_uaid()
                    echo_msg = yield S.go_type()
                    # echo_msg = yield self.S.get_orders_text(self.socket_uaid)
                    # data = "your:" + str(msg, encoding="utf-8")
                    yield self.broadcast_messages(echo_msg)
                else:
                    # 不存在或是没有登陆
                    echo_msg = '-1,-2,0,0,0,0,0,0,0,'
                    logger.error("[Connection:read_message]no...uaid")
                    yield self.on_close()
                # self.msg_disc['echo_msg'] = echo_msg
                # logger.info("[Connection:read_message]echo_msg:%s" % echo_msg)
            else:
                logger.error("[Connection:read_message]msg,None...")
                yield self.on_close()
            # print("-5-%s" % self.msg_disc.get('uaid'))
        except Exception as e:
            logger.error("[Connection:read_message]uaid:%s, error:%s" % (self.msg_disc.get('uaid'),e))
            # yield self.remove_clients_state()
            # yield self.broadcast_messages('-1,0,0,0,0,0,0,0,0,')

    @gen.coroutine
    def close_same_uaid(self):
        try:
            None_conn_list = []
            for clients_conn in Connection.clients:
                # print("chick_conn:%s" % conn.socket_uaid)
                if clients_conn.msg_disc.get('uaid') == 0:
                    None_conn_list.append(clients_conn)
                    continue
                if clients_conn.msg_disc.get('uaid') == self.msg_disc.get('uaid'):
                    if clients_conn._address != self._address:
                        # Connection.clients.remove(clients_conn)
                        None_conn_list.append(clients_conn)
                        # yield self.on_close_Manual(clients_conn)
            if len(None_conn_list) > 0:
                logger.info("[Connection:close_same_uaid]None_conn.close_strat....")
                for clients_conn in None_conn_list:
                    yield self.on_close_Manual(clients_conn)
                        # logger.info("[Connection:close_same_uaid]%s,%s" % (clients_conn.msg_disc['uaid'], clients_conn._address))
            return
        except Exception as e:
            logger.error("[Connection:close_same_uaid]error:%s" % e)
        return

    @gen.coroutine
    def broadcast_messages(self, data):
        try:
            if self.msg_disc.get('type') == "copyorder":
                logger.info("chick_me:%s" % self.msg_disc.get('uaid'))
                yield self.send_message(data, self.msg_disc.get('uaid'))
            elif self.msg_disc.get('type') == "order":
                logger.info("order_send:%s" % self.msg_disc.get('uaid'))
                yield self.send_message(data, self.msg_disc.get('uaid'))
                # logger.info("send_A:%s" % data)
                # from handlers.myredis.redis_class import RedisClass
                # R = RedisClass()
                S = MySocketModel()
                if int(float(S.RH.get(config.redis_ua_pid_endtime + str(self.msg_disc['uaid'])))) - time.time() > 0:
                    # 在有效期内
                    S = MySocketModel()
                    data2 = yield S.get_orders_sql_text(self.msg_disc['uaid'])
                    # logger.info("send_B:%s" % data2)
                    for clients_conn in Connection.clients:
                        # print("chick_conn:%s" % clients_conn.msg_disc.get('uaid'))
                        if clients_conn.msg_disc.get('uaid') != None:
                            if clients_conn.msg_disc.get('uaid') > 0 and clients_conn.msg_disc.get('uaid') != self.msg_disc.get('uaid'):
                                flag = yield S.chick_MaterAuthorize(self.msg_disc.get('uaid'), clients_conn.msg_disc.get('uaid'))
                                if flag:
                                    # logger.info("chick_conn_OK:%s,%s" % (clients_conn.msg_disc['uaid'], clients_conn._address))
                                    clients_conn.send_message(data2, clients_conn.msg_disc.get('uaid'))
                                else:
                                    logger.error("chick_conn_UaidNoAuthorize:%s" % (clients_conn._address,))
                        else:
                            logger.error("chick_conn_NO2:%s" % (clients_conn._address,))
                else:
                    logger.info("[Connection:broadcast_messages] Expired")
                # print("User said:", data, self._address)
            else:
                yield self.send_message("", None)
            if self.msg_disc.get('uaid') != None:
                if self.msg_disc.get('uaid') > 0:
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
        except Exception as e:#iostream.StreamClosedError
            logger.error("[Connection:broadcast_messages]error:%s" % e)

    @gen.coroutine
    def send_message(self, data, uaid):
        try:
            logger.info("[sendTo]{uaid}:%s, {IP}:%s" % (uaid, self._address))#{data}:%s , data
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
            logger.info("[Connection:on_close]A user out: %s" % (self._address,))
            # print("close:%s" % (not self._stream.closed()))
            # print(Connection.clients(self))#
            # Connection.clients.close(self)
            # Connection.clients.
            if not self._stream.closed():
                self._stream.close()
                self.remove_clients_state()
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
            logger.info("[on_close_Manual]A user out: %s" % (clients_conn._address,))
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
                if self.clients_state == True:
                    Connection.clients.remove(self)
                    self.clients_state = False
                    logger.info("[remove_clients_state:self]remove:%s" % (self._address,))
            else:
                if clients_conn.clients_state == True:
                    Connection.clients.remove(clients_conn)
                    clients_conn.clients_state = False
                    logger.info("[remove_clients_state:clients_conn]remove:%s" % (clients_conn._address,))
        except Exception as e:
            logger.error("[Connection:remove_clients_state]error:%s" % e)


class CopyServer(TCPServer):

    @gen.coroutine
    def handle_stream(self, stream, address):
        # stream.socket.settimeout(10)

        try:
            logger.info("New connection :%s,%s" % (address, stream))
            C = Connection(stream, address)
            logger.info("connection num is:%s" % len(C.clients))
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
            logger.error("[CopyServer:handle_stream]%s" % err)
            # return