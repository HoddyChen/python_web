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
import threading

client_id = 0
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
logInit_socket_client(log_path)
logger = logging.getLogger('Client')
@gen.coroutine
def chick():
    logger.debug("000001000000")

@gen.coroutine
def start():
    while True:
        for conn in SocketClientModel.clients:
            yield conn.sock_while2()
            time.sleep(1)
def main():
    R = RedisClass()
    server_list = R.get_socket_sercerIP()
    # print("start_client......", client_id)
    print(server_list)
    # client_ioloop = ioloop.IOLoop.instance()
    c1 = {}
    # for i in range(len(server_list)):
    i = 0
    a = SocketClientModel(client_id, server_list[i]['label'], server_list[i]['host'], server_list[i]['port'])
    a.start()
    # c1 = SocketClientModel(client_id)
    #     yield c1["c"+str(i)].sock_while()
    #     pass

    # yield c1.chick(TotalConsoleDist)
    # yield c1.sock_while()
    # client_ioloop.add_handler(ioloop.IOLoop.READ)
    # client_ioloop.start()
    # client_ioloop.run_sync(start)
        # if c1.stream.closed():
        #     yield c1.chick(TotalConsoleDist)
        # else:
        #     break
    # run_client()
    print("exit")
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
    def __init__(self, client_id, label, host, port):
        SocketClientModel.clients.add(self)
        self.label = label
        self.client_id = client_id
        self.host = host
        self.port = port
        self.flag = False
        self.time_vol = 0
        self.MD5info = "WZ12KfOkMIbwXiRm84gGIUHGEPie4klyX"
        # self.R = RedisClass()
        # self.io_loop = io_loop

        # self.connect()
        # self.receive_message()
        # self.sock_while()

    @gen.coroutine
    def sock_while2(self):
        # 循环
        # yield self.connect()
        try:
            if (not self.flag) or self.stream._closed:
            # if self.stream._closed:
                for i in range(3):
                    conn_flag = yield self.connect()
                    if conn_flag:
                        break
                    else:
                        time.sleep(10)
            if self.time_vol == 0:
                logger.debug("ChickStatus:%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                yield self.send_message()
                self.time_vol = int(time.time())
            # time.sleep(1)
            # self.time_vol += 1
            if time.time() - self.time_vol > 5*55:
                self.time_vol = 0
                # print("_closed:", self.stream._closed)
                # print("closed():", self.stream.closed())
            yield self.receive_message()
            # yield self.sock_while()
        except Exception as e:
            logger.error("[SocketClientModel:sock_while]error:%s" % e)

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
                            time.sleep(10)
                if self.time_vol == 0:
                    logger.debug("ChickStatus:%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                    yield self.send_message()
                    self.time_vol = int(time.time())
                # time.sleep(1)
                # self.time_vol += 1
                if time.time() - self.time_vol > 0.5*55:
                    self.time_vol = 0
                    print("=============")
                    # print("_closed:", self.stream._closed)
                    # print("closed():", self.stream.closed())
                # yield self.receive_message()
                # yield self.sock_while()
            except Exception as e:
                logger.error("[SocketClientModel:sock_while]error:%s" % e)

    @gen.coroutine
    def connect(self):
        try:
            time0 = time.time()
            # sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            # self.stream = iostream.IOStream(sock_fd)
            self.stream = yield TCPClient().connect(self.host, int(self.port))
            # self.stream.set_close_callback(self.on_receive)
            # self.stream.connect((self.host, int(self.port)))
            logger.debug("connect_Time:%s" % (time.time()-time0))
            self.flag = True
            self.time_vol = 0
            # yield self.start()
            # yield self.receive_message()
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
    # @gen.coroutine
    def start(self):
        t1 = threading.Thread(target=self.read_message)
        t2 = threading.Thread(target=self.sock_while)
        # t1.daemon, t2.daemon = True, True
        t1.setDaemon(True)
        t2.setDaemon(True)
        t1.start()
        t2.start()

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
            self.time_vol = int(time.time())
            yield self.stream.write(msg_str)
            logger.debug("send_message:%s" % msgDist)
            yield self.receive_message()
            self.time_vol = int(time.time())
            return
        except Exception as e:
            logger.error("[SocketClientModel:send_message]error:%s" % e)

    @gen.coroutine
    def client_send_message(self, msgDist={}):
        # 处理指令待发送数据
        if msgDist == {}:
            msgDist["sendid"] = 0
            msgDist["followid"] = 0
            msgDist["fx_type"] = "ChickStatus"
        source_label = msgDist['label']
        for conn in SocketClientModel.clients:
            if conn.label == source_label:
                break
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
    def read_message(self):
        while True:
            self.receive_message()

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
                        logger.info("[SocketClientModel:receive_message:ReturnStatus]$s:followid:%s,sendid:%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg_disc['followid'], msg_disc['sendid']))
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
            print(time.time()-self.time_vol)
            # yield self.receive_message
        except Exception as e:
            logger.error("[SocketClientModel:receive_message]tcp client exception:%s" % e)
        finally:
            # yield self.sock_while()
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

if __name__ == '__main__':
    main()
    # while True:
    # chick_redisConsole()
