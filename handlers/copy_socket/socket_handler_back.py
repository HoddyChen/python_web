# coding=utf-8
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from tornado import ioloop, gen, iostream
from models.my_socket.my_socket_model import MySocketModel
import logging
import config

logger = logging.getLogger('Socket')
class Connection(object):
    clients = set()

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self.msg_disc = {}
        self._stream.set_close_callback(self.on_close)
        # self.S = MySocketModel()
        self.read_message()
        logger.info("A new user entered.%s" % str(address))

    @gen.coroutine
    def read_message(self):
        # try:
        msg = yield self._stream.read_until(bytes("\n", encoding="utf8"))
        # IOLoop.current().call_at(IOLoop.current().time() + 5, lambda: self.broadcast_messages('ok 5\n'))
        print(msg)
        if msg != "":
            logger.info("msg:%s" % msg)
            # 验证用户
            S = MySocketModel()
            self.msg_disc = yield S.chick_user(msg)
            logger.info("uaid:%s" % self.msg_disc['uaid'])
            if self.msg_disc['uaid'] > 0:
                echo_msg = yield S.go_type()
                # echo_msg = yield self.S.get_orders_text(self.socket_uaid)
                # data = "your:" + str(msg, encoding="utf-8")
            else:
                # 不存在或是没有登陆
                echo_msg = '-1,-2,0,0,0,0,0,0,0,'
            # self.msg_disc['echo_msg'] = echo_msg
            yield self.broadcast_messages(echo_msg)
        # else:
        #     self.read_message()
        # except iostream.StreamClosedError as e:
        # except Exception as e:
        #     logger.error("[Connection:read_message]error:%s" % e)
        #     yield self.on_close()
        #     pass

    @gen.coroutine
    def broadcast_messages(self, data):
        # try:
        if self.msg_disc['type'] == "copyorder":
            yield self.send_message(data + "\n")
            logger.info("chick:%s" % data)
        elif self.msg_disc['type'] == "order":
            yield self.send_message(data + "\n")
            logger.info("send_A:%s" % data)
            # from handlers.myredis.redis_class import RedisClass
            # R = RedisClass()
            S = MySocketModel()
            import time
            if int(float(S.RH.get(config.redis_ua_pid_endtime + str(self.msg_disc['uaid'])))) - time.time() > 0:
                # 在有效期内
                S = MySocketModel()
                data2 = yield S.get_orders_sql_text(self.msg_disc['uaid'])
                logger.info("send_B:%s" % data2)
                for conn in Connection.clients:
                    # print("chick_conn:%s" % conn.socket_uaid)
                    flag = yield S.chick_MaterAuthorize(self.msg_disc['uaid'], conn.msg_disc['uaid'])
                    if flag:
                        logger.info("chick_conn_OK:%s,%s" % (conn.msg_disc['uaid'], conn._address))
                        conn.send_message(data2 + "\n")
                    else:
                        logger.info("chick_conn_NO:%s,%s" % (conn.msg_disc['uaid'], conn._address))
            else:
                logger.info("broadcast_messages: Expired")
            # print("User said:", data, self._address)
        else:
            yield self.send_message("" + "\n")
        logger.info("----------------")
        if self.msg_disc['uaid'] > 0:
            yield self.read_message()
        else:
            yield self.on_close()
        # except iostream.StreamClosedError as e:
        # except Exception as e:
        #     logger.error("[Connection:broadcast_messages]error:%s" % e)
        #     # yield self.on_close()
        #     pass

    @gen.coroutine
    def send_message(self, data):
        try:
            yield self._stream.write(bytes(data, encoding="utf8"))
        except iostream.StreamClosedError as e:
            logger.error("[Connection:send_message]error:%s" % e)
            # yield self.on_close()
            pass


    # @gen.coroutine
    # def get_SocketQueue(self):
    #     # 返回要发送的文字
    #     queue_flag = yield self.S.chick_SocketQueue(self.socket_uaid)
    #     # print("queue_flag%s" % queue_flag)
    #     if queue_flag == True:
    #         import time
    #         print(time.time())
    #         echo_msg = yield self.S.get_orders_text(self.socket_uaid)
    #         yield self.broadcast_messages(echo_msg)
    #         yield self.S.delSocketQueue(self.socket_uaid)
    #
    #     return

    @gen.coroutine
    def on_close(self):
        try:
            logger.info("A user out: %s" % self._address)
            # if not self._stream.closed():
            Connection.clients.remove(self)
        except iostream.StreamClosedError as e:
            logger.error("[Connection:on_close]error:%s" % e)


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