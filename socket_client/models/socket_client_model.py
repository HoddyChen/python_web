# coding = utf-8
import struct
import logging
import socket
from tornado import ioloop, gen, iostream
# from tornado.tcpclient import TCPClient
from handlers.myredis.redis_class import RedisClass
import json
from models.public.headers_model import DistMD5
import config


class SocketClientModel(object):
    def __init__(self, logger, client_id, io_loop=None):
        self.client_id = client_id
        self.host = config.server_list[client_id]['url']
        self.port = config.server_list[client_id]['port']
        self.flag = False
        self.time_vol = 0
        self.MD5info = "WZ12KfOkMIbwXiRm84gGIUHGEPie4klyX"
        self.R = RedisClass()
        self.io_loop = io_loop
        self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = iostream.IOStream(self.sock_fd)
        self.stream.set_close_callback(self.on_receive)
        self.logger = logger

    @gen.coroutine
    def start(self, msgDist):
        self.stream.connect((self.host, self.port))
        yield self.send_message(msgDist)

        return

    @gen.coroutine
    def send_message(self, msgDist):
        # 处理待发送数据
        msgDist["sendid"] = int(msgDist["sendid"])
        msgDist["followid"] = int(msgDist["followid"])
        msgDist['label'] = str(self.client_id)
        msgDist['key2'] = config.ServerMd5Info
        try:
            msgDist['key'] = DistMD5.encryptDist(msgDist)
            # 发送数据
            yy = bytes(json.dumps(msgDist) + "\n", encoding="utf8")
            yield self.stream.write(yy)
            self.logger.info("send_message:%s" % msgDist)
            yield self.receive_message()
        except Exception as e:
            self.logger.error("[SocketClientModel:send_message]error:%s" % e)
            yield self.on_receive()

    @gen.coroutine
    def receive_message(self):
        """
        接收数据
        """
        try:
            msg = yield self.stream.read_until(bytes("\n", encoding="utf8"))
            if msg != "":
                msg = msg[:-6]
                self.logger.info("[chick_user]read:%s" % msg)
                msg_disc = json.loads(msg)
                if DistMD5.chickDist(msg_disc):
                    # self.time_vol = int(time.time())
                    # logger.debug("return:%s" % msg_disc['return'])
                    if msg_disc['return'] >= 0:
                        # if msg_disc['fx_type'] == "MakeUpOrder":
                        self.logger.info("UpOrder,set_Ok")
                        # yield self.R.set_EndTotalConsole(self.client_id)
                        # elif msg_disc['fx_type'] == "MakeOpenOrder":
                        #     logger.debug("OpenOrder,set_Ok")
                        #     yield self.R.set_EndTotalConsole(self.client_id)
                        # else:
                        #     yield self.R.set_ErrTotalConsole(self.client_id)
                        #     logger.error("fx_type error:", msg_disc['fx_type'])
                    else:
                        # yield self.R.set_ErrTotalConsole(self.client_id)
                        self.logger.info("return<0,%s" % msg_disc['return'])
                    # logger.debug("receive data:%s" % msg_disc)
                yield self.on_receive()
                return
            else:
                yield self.receive_message()
        except Exception as e:
            self.logger.info("tcp client exception:%s" % e)
            return

    @gen.coroutine
    def on_receive(self):
        if not self.stream.closed():
            self.logger.info("Received,close")
            self.stream.close()
            self.on_close()

    def on_close(self):
        # if self.shutdown:
        self.io_loop.stop()