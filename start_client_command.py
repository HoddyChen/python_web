# coding = utf-8
import logging
import os
import socket
from tornado import ioloop, gen, iostream
from tornado.tcpclient import TCPClient
from handlers.log.mylog import logInit_socket_client
from models.public.headers_model import DistMD5
# from socket_client.models.socket_client_model import SocketClientModel
import config
import time
from handlers.myredis.redis_class import RedisClass
import json
from models.public.headers_model import global_Models

client_id = 0
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
logInit_socket_client(log_path)
logger = logging.getLogger('Client')
G = global_Models()
G.set_map("main_num", 0)
R = RedisClass()
def main():

    server_list = R.get_socket_sercerIP()
    # print("start_client......", client_id)
    G.set_map("main_num", G.get("main_num") + 1)
    client_ioloop = ioloop.IOLoop.instance()
    c1 = {}
    for i in range(len(server_list)):
        c1[server_list[i]['label']] = SocketClientModel(client_id, server_list[i]['label'], server_list[i]['host'], server_list[i]['port'], client_ioloop)
    client_ioloop.start()
    # client_ioloop.stop()
    # client_ioloop.close()
    # time.sleep(30)
    # if G.get("main_num") > 3:
    #     time.sleep(10)
    #     if G.get("main_num") > 6:
    #         G.set_map("main_num", 0)
    logger.error("client_ioloop exit.")
    # exit()
    # except Exception as e:
    #     print("err:", e)

# def chick_redisConsole():
#     # print("2")
#     try:
#         # print(config.server_list[client_id]['url'], config.server_list[client_id]['port'])
#         # R = RedisClass()
#         print("0:")
#         TotalConsoleDist = {'senduuu':""}
#         if TotalConsoleDist:
#             # 发送命令
#             print("1:")
#             # print("Time:%s,%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),TotalConsoleDist))
#             send_client(TotalConsoleDist)
#     except Exception as e:
#         print("err:", e)

# def send_client(TotalConsoleDist):
#     client_ioloop = ioloop.IOLoop.instance()
#     c1 = SocketClientModel(client_id, client_ioloop)
#     client_ioloop.start()
#     try:
#         while(True):
#             yield c1.chick(TotalConsoleDist)
#     except Exception as e:
#         yield c1.on_receive()


class SocketClientModel(object):
    stream = {}
    clients = set()
    def __init__(self, client_id, label, host, port, io_loop):
        SocketClientModel.clients.add(self)
        self.label = label
        self.client_id = client_id
        self.host = host
        self.port = port
        self.flag = False
        self.time_vol = 0
        self.io_loop = io_loop
        self.sock_fd = None
        self.stream = None
        self.G = global_Models()
        if self.G.get("msg_list"):
            self.msgDist = eval(self.G.get("msg_list"))
        else:
            self.msgDist = {}
        # self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        # self.stream = iostream.IOStream(self.sock_fd)
        # self.stream.set_close_callback(self.on_receive)
            # self.msgDist = {}
        # self.connect()
        # self.receive_message()
        self.sock_while()

    @gen.coroutine
    def sock_while(self):
        # 循环
        while(True):
            try:
                if (not self.flag) or self.stream._closed:
                    conn_flag = yield self.connect()
                    if conn_flag:
                        break
                    else:
                        time.sleep(5)
                # if self.time_vol == 0:
                #     logger.debug("ChickStatus:%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                #     yield self.send_message()
                #     self.time_vol = int(time.time())
                # time.sleep(1)
                # self.time_vol += 1
                # if time.time() - self.time_vol > 5*55:
                #     self.time_vol = int(time.time())
                #     yield self.send_message()
                    # print("_closed:", self.stream._closed)
                    # print("closed():", self.stream.closed())

                # yield self.sock_while()
            except Exception as e:
                logger.error("[SocketClientModel:sock_while]error:%s" % e)
        yield self.send_message()
        # yield self.receive_message()

    @gen.coroutine
    def connect(self):
        try:
            time0 = time.time()
            self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.stream = iostream.IOStream(self.sock_fd)
            self.stream.set_close_callback(self.on_receive)
            self.stream.connect((self.host, int(self.port)))
            logger.debug("connect_Time:%s" % (time.time()-time0))
            self.flag = True
            # self.time_vol = 0
            logger.debug("connect client...%s" % (self.host + ":" + self.port,))
            return True
        except Exception as e:
            logger.error("[SocketClientModel:connect]error:%s" % e)
            self.flag = False
            return False

    #  @gen.coroutine
    # def chick(self, msgDist):
    #     yield self.send_message(msgDist)
    #     return

    #整理发送的数据
    @gen.coroutine
    def sort_data(self, msg_dist={}):
        self.time_vol = time.time()
        if msg_dist == {}:
            msg_dist = self.msgDist
        if msg_dist == {}:
            msg_dist["sendid"] = 0
            msg_dist["followid"] = 0
            msg_dist["fx_type"] = "ChickStatus"
            msg_dist['label'] = self.client_id
        if msg_dist.get('label'):
            source_label = msg_dist['label']
        else:
            source_label = self.client_id
        msg_dist['label'] = self.client_id
        msg_dist['key2'] = config.ServerMd5Info
        msg_dist['key'] = DistMD5.encryptDist(msg_dist)
        # 发送数据
        msg_str = bytes(json.dumps(msg_dist) + "\n", encoding="utf8")
        return msg_str, source_label

    @gen.coroutine
    def send_message(self, msg_dist={}):
        # 处理待发送数据
        try:
            msg, msg_label = yield self.sort_data(msg_dist)
            if not self.stream.closed():
                yield self.stream.write(msg)
                logger.debug("send_message:(%s S)%s" % ((time.time() - self.time_vol), msg))
            else:
                raise("==stream.closed")
            yield self.receive_message()
        except Exception as e:
            logger.error("[SocketClientModel:send_message]error:%s" % e)
        #     yield self.on_receive()

    @gen.coroutine
    def client_send_message(self, msg_dist={}):
        # 处理指令待发送数据
        msg_str, source_label = yield self.sort_data(msg_dist)
        for conn in SocketClientModel.clients:
            if conn.label == source_label:
                continue
            try:
                # 发送数据
                conn.stream.write(msg_str)
                logger.debug("[SocketClientModel:client_send_message:send_message]to:%s: %s" % (conn.label, self.msgDist))
                # yield conn.receive_message()
            except Exception as e:
                logger.error("[SocketClientModel:client_send_message:label:%s]error:%s" % (conn.label, e))
                # yield conn.on_receive()
        logger.debug("[SocketClientModel:client_send_message](%s)S" % (time.time()-self.time_vol,))

    @gen.coroutine
    def receive_message(self):
        # 接收数据
        try:
            time_out = time.time()
            # while(True):
            msg = yield self.stream.read_until(bytes("\n", encoding="utf8"))
            if msg != "":
                msg = msg[:-6]
                logger.debug("[SocketClientModel:receive_message](%s S)read:%s" % (time.time()-self.time_vol, msg))
                self.msgDist = json.loads(msg)
                if DistMD5.chickDist(self.msgDist):
                    # self.time_vol = int(time.time())
                    # logger.debug("return:%s" % msg_disc['return'])
                    if self.msgDist['fx_type'] == "MakeUpOrder":
                        logger.debug("UpOrder,set_Ok")
                        yield self.client_send_message(self.msgDist)
                        # yield self.R.set_EndTotalConsole(self.client_id)
                        msg_dist = self.msgDist
                        msg_dist['fx_type'] = "ReturnStatus"
                        msg_dist['return'] = 5
                        yield self.send_message(msg_dist)
                    elif self.msgDist['fx_type'] == "MakeUpPriceOrder":
                        logger.debug("UpPriceOrder,set_Ok")
                        yield self.client_send_message(self.msgDist)
                        # yield self.R.set_EndTotalConsole(self.client_id)
                        msg_dist = self.msgDist
                        msg_dist['fx_type'] = "ReturnStatus"
                        msg_dist['return'] = 5
                        yield self.send_message(msg_dist)
                    elif self.msgDist['fx_type'] == "MakeOpenOrder":
                        logger.debug("OpenOrder,set_Ok")
                        yield self.client_send_message(self.msgDist)
                        msg_dist = self.msgDist
                        msg_dist['fx_type'] = "ReturnStatus"
                        msg_dist['return'] = 5
                        yield self.send_message(msg_dist)
                        # yield self.R.set_EndTotalConsole(self.client_id)
                    elif self.msgDist['fx_type'] == "ChickStatus":
                        # logger.error("[SocketClientModel:receive_message]ChickStatus,%s" % self.msgDist.get('return'))
                        # yield self.R.set_EndTotalConsole(self.client_id)
                        self.msgDist['fx_type'] = "ReturnStatus"
                        yield self.send_message(self.msgDist)
                        self.msgDist = {}
                    elif self.msgDist['fx_type'] == "ReturnStatus":
                        logger.info("[SocketClientModel:receive_message:ReturnStatus]%s:followid:%s,sendid:%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.msgDist['followid'], self.msgDist['sendid']))
                        # yield self.sock_while()
                        self.msgDist = {}
                    else:
                        # yield self.R.set_ErrTotalConsole(self.client_id)
                        logger.error("[[SocketClientModel:receive_message:fx_type] error:%s" % self.msgDist['fx_type'])
                        self.msgDist = {}
                    # logger.debug("receive data:%s" % msg_disc)
                # yield self.on_receive()
                # break
            else:
                if time.time() - time_out > 5:
                    logger.error("[SocketClientModel:receive_message:out_time]:%s S", time.time() - time_out)
                    # break
            yield self.receive_message()
        except Exception as e:
            logger.error("[SocketClientModel:receive_message]tcp client exception:%s" % e)
            # yield self.on_receive()

    @gen.coroutine
    def on_receive(self):
        # if not self.stream.closed():
        #     logger.info("Received,close")
        #     self.stream.close()
        try:
            logger.debug("Received,close")
            # if not self.stream.closed():
            #     self.stream.close()
            # for conn in SocketClientModel.clients:
            #     if conn.stream:
            #         if not conn.stream.closed():
            #             conn.stream.close()
            #         # conn.stream = None
            #     conn.io_loop.stop()
            self.G.set_map("msg_list", self.msgDist)
            # self.on_close()
        except Exception as e:
            logger.error("[on_receive:err]:%s" % e)
        finally:
            self.flag = False
            time.sleep(5)
            yield self.sock_while()
            # yield self.on_close()

    @gen.coroutine
    def on_close(self):
        # if self.shutdown:
        # print("[on_close]%s" % time.time())
        self.io_loop.stop()

if __name__ == '__main__':

    while True:
        main()
