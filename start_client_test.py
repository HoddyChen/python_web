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

# logger = logging.getLogger('Client')
logger = logging.getLogger('Socket')
c1 = None
def main():
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    logInit_socket_client(log_path)

class ClientClassModel():
    pass

class SocketClientModel(object):
    clients = set()
    handshake_type = ""
    def __init__(self, *args):
        self.client_list = args[0]
        # self.MD5info = "WZ12KfOkMIbwXiRm84gGIUHGEPie4klyX"

    @gen.coroutine
    def ClientHandshake(self, handshake_type):
        # SocketClientModel.handshake_type = handshake_type
        for clientIP in self.client_list:
            flag = 0
            for conn in SocketClientModel.clients:
                if clientIP["url"] == conn.host and clientIP["port"] == conn.port:
                    if (not conn.flag) or conn.stream._closed:
                        # self.on_receive(conn)
                        SocketClientModel.clients.remove(conn)
                    else:
                        # 直接发送
                        flag = 1
                        yield self.ClientSeletType(handshake_type, conn)
                        yield self.close_over_client(conn)
                    break
            if flag == 0:
                # 重新连接
                conn2 = yield self.connect(clientIP)
                yield self.ClientSeletType(handshake_type, conn2)

    @gen.coroutine
    def close_over_client(self, conn):
        # 删除多余的连接
        for conn2 in SocketClientModel.clients:
            if conn2.host == conn.host and conn2.port == conn.port:
                if conn2.stream.socket.getsockname() != conn.stream.socket.getsockname():
                    self.on_receive(conn2)

    @gen.coroutine
    def ClientSeletType(self, handshake_type, conn):
        if handshake_type == "Keep":
            # 保持连接
            # print("old:new-%s:%s"% (self.time_vol,time.time()))
            if conn.time_vol == None or time.time() - conn.time_vol > 100:
                logger.debug("old:new-%s:%s" % (conn.time_vol, time.time()))
                # 发送保持信息
                conn.time_vol = time.time()
                logger.debug("Keep:%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                yield self.send_message({'senduuu': time.time()}, conn)
        elif handshake_type == "Distributing":
            # 分发信息
            logger.debug("Distributing:%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            yield self.send_message({'senduuu': int(time.time())}, conn)
        else:
            logger.error("[SocketClientModel:ClientHandshake]handshake_type is null")
        # yield self.connect()
        return

    @gen.coroutine
    def connect(self, clientIP):
        try:
            ClientClassModel.client_id = clientIP['id']
            ClientClassModel.host = clientIP["url"]
            ClientClassModel.port = clientIP["port"]
            ClientClassModel.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            ClientClassModel.stream = iostream.IOStream(ClientClassModel.sock_fd)
            ClientClassModel.stream.set_close_callback(self.on_receive)
            yield ClientClassModel.stream.connect((clientIP["url"], clientIP["port"]))
            ClientClassModel.flag = True
            ClientClassModel.time_vol = 0
            SocketClientModel.clients.add(ClientClassModel)
            logger.debug("[SocketClientModel:connect]connect client...%s-->%s" % (ClientClassModel.stream.socket.getsockname(), ClientClassModel.stream.socket.getpeername()))
            return ClientClassModel
        except Exception as e:
            ClientClassModel.flag = False
            logger.error("[SocketClientModel:connect]error:%s" % e)

    @gen.coroutine
    def send_message(self, msgDist, conn):
        # 处理待发送数据
        msgDist["sendid"] = 2
        msgDist["followid"] = 1
        msgDist["fx_type"] = "ChickStatus"
        msgDist['id'] = conn.client_id
        msgDist['key2'] = config.ServerMd5Info
        try:
            msgDist['key'] = DistMD5.encryptDist(msgDist)
            # 发送数据
            logger.debug("[SocketClientModel:send_message]strat:%s-->%s" % (conn.stream.socket.getsockname(), conn.stream.socket.getpeername()))
            yy = bytes(json.dumps(msgDist) + "\n", encoding="utf8")
            yield conn.stream.write(yy)
            # yield self.stream.shutdown(1)
            logger.debug("[SocketClientModel:send_message]write:%s" % msgDist)
            yield self.receive_message(conn)
        except Exception as e:
            logger.error("[SocketClientModel:send_message]error:%s" % e)
            conn.flag = False
            # self.on_receive(conn)

    @gen.coroutine
    def receive_message(self, conn):
        """
        接收数据
        """
        try:
            time_out = time.time()
            msg = yield conn.stream.read_until(bytes("\n", encoding="utf8"))
            if msg != "":
                msg = msg[:-6]
                logger.debug("[SocketClientModel:chick_user]read:%s" % msg)
                msg_disc = json.loads(msg)
                if DistMD5.chickDist(msg_disc):
                    # self.time_vol = int(time.time())
                    # logger.debug("return:%s" % msg_disc['return'])
                    if msg_disc['return'] >= 0:
                        if msg_disc['fx_type'] == "MakeUpOrder":
                            logger.debug("[SocketClientModel:UpOrder],set_Ok")
                            # yield self.R.set_EndTotalConsole(self.client_id)
                        elif msg_disc['fx_type'] == "MakeOpenOrder":
                            logger.debug("[SocketClientModel:OpenOrder],set_Ok")
                            # yield self.R.set_EndTotalConsole(self.client_id)
                        elif msg_disc['fx_type'] == "ChickStatus":
                            logger.debug("[SocketClientModel:ChickStatus],set_Ok")
                            # yield self.R.set_EndTotalConsole(self.client_id)
                        else:
                            # yield self.R.set_ErrTotalConsole(self.client_id)
                            logger.error("[SocketClientModel:receive_message] fx_type-error:%s" % msg_disc['fx_type'])
                    else:
                        # yield self.R.set_ErrTotalConsole(self.client_id)
                        logger.error("[SocketClientModel:receive_message]return:%s" % msg_disc['return'])
                    # logger.debug("receive data:%s" % msg_disc)
                # yield self.on_receive()
                # break
            else:
                logger.error("[SocketClientModel:receive_message]out_time:%.2f S" % time.time() - time_out)
                    # break
            conn.time_vol = time.time()
            logger.debug("[SocketClientModel,updata-time]%s{%s}" % (conn.stream.socket.getsockname(), conn.time_vol))
            return
        except Exception as e:
            logger.error("[SocketClientModel:receive_message]tcp client exception:%s" % e)
            conn.flag = False
            # self.on_receive(conn)
            return

    @gen.coroutine
    def on_receive(self, conn):
        # if not self.stream.closed():
        #     logger.info("Received,close")
        #     self.stream.close()
        try:
            logger.debug("[SocketClientModel:on_receive]stream.close")
            conn.stream.close()
            self.on_close(conn)
        except Exception as e:
            logger.error("[on_receive:err]:%s" % e)
            return
        # finally:
        #     conn.flag = False
        #     # yield self.on_close()

    @gen.coroutine
    def on_close(self, conn):
        # if self.shutdown:
        # self.io_loop.stop()
        pass

if __name__ == '__main__':
    main()
    # while True:
    # chick_redisConsole()
    run_client2()
    time.sleep(0.002)