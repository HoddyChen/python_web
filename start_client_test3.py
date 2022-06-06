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
# from handlers.myredis.redis_class import RedisClass
import json
client_id = 0
logger = logging.getLogger('Client')
c1 = None
def main():
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    logInit_socket_client(log_path)
    # R = RedisClass()
    # R.ResetTotalConsole()
    print("start_client......", client_id)

def run_client2(client_id):
    print("yy")
    try:
        # while(True):
            # print(client_ioloop)
        TotalConsoleDist = {'senduuu': ""}
        client_ioloop = ioloop.IOLoop.instance()
        c1 = SocketClientModel(client_id, client_ioloop)
        # c1 = SocketClientModel(client_id)
        c1.sock_while()
        # yield c1.chick(TotalConsoleDist)
        # yield c1.sock_while()
        client_ioloop.start()
            # if c1.stream.closed():
            #     yield c1.chick(TotalConsoleDist)
            # else:
            #     break
        # run_client()
        print("exit")
    except Exception as e:
        print("err:", e)

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
    def __init__(self, client_id, io_loop):
        self.client_id = client_id
        self.host = config.server_list[client_id]['url']
        self.port = config.server_list[client_id]['port']
        self.flag = False
        self.time_vol = 0
        self.MD5info = "WZ12KfOkMIbwXiRm84gGIUHGEPie4klyX"
        # self.R = RedisClass()
        self.io_loop = io_loop
        self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = iostream.IOStream(self.sock_fd)
        print(type(self.stream))
        self.stream.set_close_callback(self.on_receive)
        # self.sock_while()

    @gen.coroutine
    def sock_while(self):
        # 循环
        self.time_vol = 0
        # yield self.connect()
        while(True):
            try:
                if (not self.flag) or self.stream._closed:
                # if self.stream._closed:
                    yield self.connect()
                if self.time_vol == 0:
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    yield self.chick({'senduuu':"123"})
                    self.time_vol = time.time()
                time.sleep(1)
                # self.time_vol += 1
                if time.time() - self.time_vol > 1*55:
                    self.time_vol = 0
                    print("_closed:", self.stream._closed)
                    print("closed():", self.stream.closed())
            except Exception as e:
                logger.error("[SocketClientModel:sock_while]error:%s" % e)

    @gen.coroutine
    def connect(self):
        try:
            self.stream.connect((self.host, self.port))
            # print("connect_Status:%s" % yy)
            self.flag = True
            print("connect client...")
        except Exception as e:
            logger.error("[SocketClientModel:connect]error:%s" % e)

    @gen.coroutine
    def chick(self, msgDist):
        yield self.send_message(msgDist)
        return

    @gen.coroutine
    def send_message(self, msgDist):
        # 处理待发送数据
        msgDist["sendid"] = 0
        msgDist["followid"] = 0
        msgDist["fx_type"] = "ChickStatus"
        msgDist['label'] = self.client_id
        msgDist['key2'] = config.ServerMd5Info
        try:
            msgDist['key'] = DistMD5.encryptDist(msgDist)
            # 发送数据
            yy = bytes(json.dumps(msgDist) + "\n", encoding="utf8")
            # yy = b"ooooooooooo"
            self.time_vol = time.time()
            yield self.stream.write(yy)
            # yield self.stream.shutdown(1)
            logger.debug("send_message:%s" % msgDist)
            yield self.receive_message()
        except Exception as e:
            logger.error("[SocketClientModel:send_message]error:%s" % e)

    @gen.coroutine
    def receive_message(self):
        """
        接收数据
        """
        try:
            time_out = time.time()
            while(True):
                msg = yield self.stream.read_until(bytes("\n", encoding="utf8"))
                if msg != "":
                    msg = msg[:-6]
                    logger.debug("[chick_user]read:%s" % msg)
                    msg_disc = json.loads(msg)
                    if DistMD5.chickDist(msg_disc):
                        # self.time_vol = int(time.time())
                        # logger.debug("return:%s" % msg_disc['return'])
                        if msg_disc['return'] >= 0:
                            if msg_disc['fx_type'] == "MakeUpOrder":
                                logger.debug("UpOrder,set_Ok")
                                # yield self.R.set_EndTotalConsole(self.client_id)
                            elif msg_disc['fx_type'] == "MakeOpenOrder":
                                logger.debug("OpenOrder,set_Ok")
                                # yield self.R.set_EndTotalConsole(self.client_id)
                            elif msg_disc['fx_type'] == "ChickStatus":
                                logger.debug("ChickStatus,set_Ok")
                                # yield self.R.set_EndTotalConsole(self.client_id)
                            else:
                                # yield self.R.set_ErrTotalConsole(self.client_id)
                                logger.error("fx_type error:", msg_disc['fx_type'])
                        else:
                            # yield self.R.set_ErrTotalConsole(self.client_id)
                            logger.error("return<0,", msg_disc['return'])
                        # logger.debug("receive data:%s" % msg_disc)
                    # yield self.on_receive()
                    break
                else:
                    if time.time() - time_out > 5:
                        logger.error("[receive_message:out_time]:%s S", time.time() - time_out)
                        break
            print(time.time()-self.time_vol)
            return
        except Exception as e:
            logger.error("tcp client exception:%s" % e)
            return

    @gen.coroutine
    def on_receive(self):
        # if not self.stream.closed():
        #     logger.info("Received,close")
        #     self.stream.close()
        try:
            logger.debug("Received,close")
            self.stream.close()
            self.on_close()
        except Exception as e:
            logger.error("[on_receive:err]:%s" % e)
            return
        finally:
            self.flag = False
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
    run_client2(0)
    time.sleep(0.002)