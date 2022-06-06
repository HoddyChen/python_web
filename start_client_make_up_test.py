# coding = utf-8
import logging
import os
from tornado import ioloop, gen
from tornado.tcpclient import TCPClient
from handlers.log.mylog import logInit_socket_client
from socket_client.models.socket_client_model import SocketClientModel
import config
import time
from handlers.myredis.redis_class import RedisClass
import socket
from tornado import ioloop, gen, iostream
import json
from models.public.headers_model import DistMD5

client_id = 999
R = RedisClass()
server_list = R.get_socket_sercerIP()
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
logInit_socket_client(log_path)
logger = logging.getLogger('Socket')
print("start_client......", client_id)

class SocketClientModel(object):
    # stream = {}
    clients = set()
    def __init__(self, client_id, label, host, port, io_loop):
        SocketClientModel.clients.add(self)
        self.label = label
        self.client_id = client_id
        self.host = host
        self.port = port
        self.flag = False
        self.time_vol = 0
        self.MD5info = "WZ12KfOkMIbwXiRm84gGIUHGEPie4klyX"
        self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = iostream.IOStream(self.sock_fd)
        self.stream.set_close_callback(self.on_receive)
        # self.R = RedisClass()
        self.io_loop = io_loop
        # self.msgDist = msgDist
        # self.connect()
        # self.receive_message()
        # self.sock_while()

    @gen.coroutine
    def sock_while(self):
        # 循环
        # yield self.connect()
        while(True):
            try:
                if (not self.flag) or self.stream._closed:
                # if self.stream._closed:
                    for i in range(3):
                        conn_flag = yield self.connect()
                        if conn_flag:
                            break
                        else:
                            time.sleep(60)
                if self.time_vol == 0:
                    logger.debug("ChickStatus:%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                    yield self.send_message()
                # self.time_vol = int(time.time())
                # time.sleep(1)
                # self.time_vol += 1
                if time.time() - self.time_vol > 3*55:
                    yield self.client_send_message()
                    # print("_closed:", self.stream._closed)
                    # print("closed():", self.stream.closed())
                # yield self.receive_message()
                # yield self.sock_while()
                yield self.chick_redisConsole()
                time.sleep(0.005)
                # yield self.sock_while()
            except Exception as e:
                logger.error("[SocketClientModel:sock_while]error:%s" % e)

    @gen.coroutine
    def connect(self):
        try:
            # self.time_vol = time.time()
            self.stream.connect((self.host, int(self.port)))
            # logger.debug("connect_Time:%s" % (time.time()-time0))
            self.flag = True
            self.time_vol = 0
            logger.debug("connect client...")
            return True
        except Exception as e:
            self.flag = False
            logger.error("[SocketClientModel:connect]error:%s" % e)
            return False

    # @gen.coroutine
    # def chick(self, msgDist):
    #     yield self.send_message(msgDist)
    #     return

    @gen.coroutine
    def send_message(self, msgDist={}):
        # 处理待发送数据
        if msgDist == {}:
            msgDist["sendid"] = 0
            msgDist["followid"] = 0
            msgDist["fx_type"] = "ChickStatus"
        msgDist['label'] = self.client_id
        msgDist['key2'] = config.ServerMd5Info
        try:
            msgDist['key'] = DistMD5.encryptDist(msgDist)
            # 发送数据
            msg_str = bytes(json.dumps(msgDist) + "\n", encoding="utf8")
            # self.time_vol = int(time.time())
            yield self.stream.write(msg_str)
            logger.debug("send_message:%s" % msgDist)
            yield self.receive_message()
            # self.time_vol = int(time.time())
        except Exception as e:
            logger.error("[SocketClientModel:send_message]error:%s" % e)

    @gen.coroutine
    def client_send_message(self, msgDist={}):
        # 处理指令待发送数据
        if msgDist == {}:
            msgDist["sendid"] = 0
            msgDist["followid"] = 0
            msgDist["fx_type"] = "ChickStatus"
        # source_label = msgDist['label']
        for conn in SocketClientModel.clients:
            # if conn.label == source_label:
            #     break
            msgDist['label'] = conn.client_id
            msgDist['key2'] = config.ServerMd5Info
            try:
                msgDist['key'] = DistMD5.encryptDist(msgDist)
                # 发送数据
                msg_str = bytes(json.dumps(msgDist) + "\n", encoding="utf8")
                conn.time_vol = int(time.time())
                yield conn.stream.write(msg_str)
                logger.debug("[SocketClientModel:client_send_message:send_message]to:%s: %s" % (conn.label, msgDist))
                yield conn.receive_message()
                conn.time_vol = int(time.time())
            except Exception as e:
                logger.error("[SocketClientModel:client_send_message:label:%s]error:%s" % (conn.label, e))

    @gen.coroutine
    def receive_message(self):
        """
        接收数据
        """
        try:
            time_out = time.time()
            # while(True):
            msg = yield self.stream.read_until(bytes("\n", encoding="utf8"))
            if msg != "":
                msg = msg[:-6]
                logger.debug("[SocketClientModel:receive_message]read:%s" % msg)
                msg_disc = json.loads(msg)
                if DistMD5.chickDist(msg_disc):
                    # self.time_vol = int(time.time())
                    # logger.debug("return:%s" % msg_disc['return'])
                    if msg_disc['fx_type'] == "MakeUpOrder":
                        logger.debug("UpOrder,set_Ok")
                        yield self.client_send_message(msg_disc)
                        # yield self.R.set_EndTotalConsole(self.client_id)
                        msg_disc['fx_type'] = "ReturnStatus"
                        msg_disc['return'] = 5
                        yield self.send_message(msg_disc)
                    elif msg_disc['fx_type'] == "MakeOpenOrder":
                        logger.debug("OpenOrder,set_Ok")
                        yield self.client_send_message(msg_disc)
                        msg_disc['fx_type'] = "ReturnStatus"
                        msg_disc['return'] = 5
                        yield self.send_message(msg_disc)
                        # yield self.R.set_EndTotalConsole(self.client_id)
                    elif msg_disc['fx_type'] == "ChickStatus":
                        if msg_disc.get('return') >= 0:
                            logger.debug("[SocketClientModel:receive_message]ChickStatus,set_Ok")
                        else:
                            # yield self.R.set_ErrTotalConsole(self.client_id)
                            logger.error("[SocketClientModel:receive_message]ChickStatus,return<0,", msg_disc.get('return'))
                        self.time_vol = int(time.time())
                        # yield self.R.set_EndTotalConsole(self.client_id)
                    elif msg_disc['fx_type'] == "ReturnStatus":
                        logger.info("[SocketClientModel:receive_message:ReturnStatus]%s:followid:%s,sendid:%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg_disc['followid'], msg_disc['sendid']))
                        # yield self.sock_while()

                    else:
                        # yield self.R.set_ErrTotalConsole(self.client_id)
                        logger.error("[[SocketClientModel:receive_message:fx_type] error:", msg_disc['fx_type'])

                    # logger.debug("receive data:%s" % msg_disc)
                # yield self.on_receive()
                # break
            else:
                if time.time() - time_out > 5:
                    logger.error("[SocketClientModel:receive_message:out_time]:%s S", time.time() - time_out)
                    # break
                # yield self.sock_while()
            logger.debug("[SocketClientModel]runtime:%s" % (time.time()-self.time_vol,))

        except Exception as e:
            logger.error("[SocketClientModel:receive_message]tcp client exception:%s" % e)
        finally:
            # yield self.on_receive()
            pass

    @gen.coroutine
    def on_receive(self):
        # if not self.stream.closed():
        #     logger.info("Received,close")
        #     self.stream.close()
        try:
            logger.debug("Received,close")
            self.stream.close()
            # self.on_close()
        except Exception as e:
            logger.error("[on_receive:err]:%s" % e)
            return
        finally:
            self.flag = False
            # yield self.connect()
            # yield self.on_close()

    @gen.coroutine
    def on_close(self):
        # if self.shutdown:
        self.io_loop.stop()
        self.flag = False

    @gen.coroutine
    def chick_redisConsole(self):
        try:
            TotalConsoleDist = R.pop_Console_list()
            if TotalConsoleDist:
                # 发送命令
                time0 = time.time()
                logger.debug("Time:%s,%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), TotalConsoleDist))
                yield self.client_send_message(TotalConsoleDist)
                logger.debug("[runtime]%s S" % (time.time()-time0,))
        except Exception as e:
            logger.error("[chick_redisConsole]err:%s" % e)

class SocketClientModel(object):
    pass

def send_client():
    client_ioloop = ioloop.IOLoop.instance()
    # c1 = SocketClientModel(client_id, client_ioloop)
    a = []
    for i in range(len(server_list)):
        a = SocketClientModel(client_id, server_list[i]['label'], server_list[i]['host'], server_list[i]['port'], client_ioloop)
        a.sock_while()


    # c1 = SocketClientModel(client_id)
    # c1.start(TotalConsoleDist)
    client_ioloop.start()

if __name__ == '__main__':
    # while True:
    send_client()
    time.sleep(0.002)