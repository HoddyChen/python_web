# coding = utf-8
import logging
import os
import socket
from tornado import ioloop, gen, iostream
from tornado.tcpclient import TCPClient
from handlers.log.mylog import logInit_socket_client
from models.public.headers_model import DistMD5
import config
import time
import json
from models.public.headers_model import global_Models
from models.my_socket.my_socket_model import MySocketModel

logger = logging.getLogger('Socket')
class ClientClassModel():
    pass

class SocketClientModel(object):
    clients = set()
    handshake_type = ""
    def __init__(self, *args):
        self.G = global_Models()
        self.S = MySocketModel()
        self.label = ""
        # self.MD5info = "WZ12KfOkMIbwXiRm84gGIUHGEPie4klyX"

    @gen.coroutine
    def ClientHandshake(self, msgDist):
        # SocketClientModel.handshake_type = handshake_type
        client_list = self.G.get("socket_server_set")
        sleep = 0
        for i in range(len(self.G.get("socket_server_set"))):
            if self.G.get("socket_server_set")[i]['flag'] != 1 and self.G.get("socket_server_set")[i]['me'] == 0:
                flag = 0
                for conn in SocketClientModel.clients:
                    if client_list[i]["host"] == conn.host and int(client_list[i]["port"]) == int(conn.port):
                        if (not conn.flag) or conn.stream._closed:
                            self.on_receive(conn)
                        else:
                            # 直接发送
                            flag = 1
                            yield self.ClientSeletType(client_list[i]["time_vol"], msgDist, conn)
                            yield self.close_over_client(conn)
                        break
                if flag == 0:
                    # 重新连接
                    if sleep == 1:
                        time.sleep(0.3)
                    conn2 = yield self.connect(i, self.G.get("socket_server_set"))
                    if type(conn2) != type(True):
                        yield self.ClientSeletType(self.G.get("socket_server_set")[i]["time_vol"], msgDist, conn2)
                        sleep = 1
                    elif conn2 == True:
                        # 已经有连接的情况
                        for conn3 in SocketClientModel.clients:
                            if client_list[i]["host"] == conn3.host and int(client_list[i]["port"]) == int(conn3.port):
                                if (not conn3.flag) or conn3.stream._closed:
                                    self.on_receive(conn3)
                                else:
                                    # 直接发送
                                    flag = 1
                                    yield self.ClientSeletType(self.G.get("socket_server_set")[i]["time_vol"], msgDist, conn3)
                                    yield self.close_over_client(conn3)
                                break
                    elif conn2 == False:
                        # 连接错误的情况
                        pass
        logger.debug("[SocketClientModel:ClientHandshake]send_client num is %s" % len(SocketClientModel.clients))


    @gen.coroutine
    def close_over_client(self, conn):
        # 删除多余的连接
        for conn2 in SocketClientModel.clients:
            if conn2.host == conn.host and conn2.port == conn.port:
                if conn2.stream.socket.getsockname() != conn.stream.socket.getsockname():
                    self.on_receive(conn2)
                    logger.debug("[SocketClientModel:close_over_client]%s" % conn2.stream.socket.getsockname())

    @gen.coroutine
    def ClientSeletType(self, time_vol, msgDist, conn):
        if msgDist['fx_type'] == "ChickStatus":
            # 保持连接
            # print("old:new-%s:%s"% (self.time_vol,time.time()))
            if time_vol == 0 or time.time() - time_vol > 3*55:
                logger.debug("[SocketClientModel:old:new]%s:%s[client_Num:%s]" % (time_vol, time.time(), len(SocketClientModel.clients)))
                # 发送保持信息
                # conn.time_vol = time.time()
                self.S.mark_socket_global(conn.label, 2, int(time.time()))
                logger.debug("[SocketClientModel:Keep]%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                yield self.send_message(msgDist, conn)
        elif msgDist['fx_type'] == "MakeUpOrder" or msgDist['fx_type'] == "MakeOpenOrder":
            # 分发信息
            logger.debug("[SocketClientModel:ClientSeletType]%s->%s" % (msgDist['fx_type'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            self.S.mark_socket_global(conn.label, 2, int(time.time()))
            yield self.send_message(msgDist, conn)
        else:
            logger.error("[SocketClientModel:ClientHandshake]handshake_type is null")
        # yield self.connect()
        return

    @gen.coroutine
    def connect(self, id, client_list):
        try:
            # client_list = self.G.get("socket_server_set")
            if client_list[id]['flag'] == 0:
                self.label = client_list[id]['label']
                ClientClassModel.label = client_list[id]['label']
                ClientClassModel.host = client_list[id]["host"]
                ClientClassModel.port = client_list[id]["port"]
                ClientClassModel.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                ClientClassModel.stream = iostream.IOStream(ClientClassModel.sock_fd)
                ClientClassModel.stream.set_close_callback(self.on_receive)
                yield ClientClassModel.stream.connect((client_list[id]["host"], int(client_list[id]["port"])))
                self.S.mark_socket_global(client_list[id]['label'], 2, 0)
                ClientClassModel.flag = True
                # ClientClassModel.time_vol = 0
                SocketClientModel.clients.add(ClientClassModel)
                logger.debug("[SocketClientModel:connect]connect client...%s-->%s" % (ClientClassModel.stream.socket.getsockname(), ClientClassModel.stream.socket.getpeername()))
                return ClientClassModel
            else:
                return True
        except Exception as e:
            ClientClassModel.flag = False
            self.S.mark_socket_global(client_list[id]['label'], 0, 0)
            logger.error("[SocketClientModel:connect]error:%s" % e)
            return False

    @gen.coroutine
    def send_message(self, msgDist, conn):
        # 处理待发送数据
        # msgDist["sendid"] = 2
        # msgDist["followid"] = 1
        # msgDist["fx_type"] = "ChickStatus"
        # msgDist['label'] = conn.label
        # msgDist['key2'] = config.ServerMd5Info
        try:
            # msgDist['key'] = DistMD5.encryptDist(msgDist)
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
            # conn.time_vol = time.time()
            self.S.mark_socket_global(conn.label, 2, int(time.time()))
            logger.debug("[SocketClientModel,updata-time]%s{%s}" % (conn.stream.socket.getsockname(), int(time.time())))
            yield self.receive_message(conn)
            return True
        except Exception as e:
            logger.error("[SocketClientModel:receive_message]tcp client exception:%s" % e)
            conn.flag = False
            self.S.mark_socket_global(conn.label, 0, 0)
            # self.on_receive(conn)
            return False

    @gen.coroutine
    def on_receive(self, conn=None):
        # if not self.stream.closed():
        #     logger.info("Received,close")
        #     self.stream.close()
        try:
            logger.debug("[SocketClientModel:on_receive]stream.close")
            if conn == None:
                for conn2 in SocketClientModel.clients:
                    if conn2.label == self.label:
                        conn2.stream.close()
                        self.S.mark_socket_global(self.label, 0, 0)
                        SocketClientModel.clients.remove(conn2)

            else:
                conn.stream.close()
                self.S.mark_socket_global(conn.label, 0, 0)
                SocketClientModel.clients.remove(conn)
            # self.on_close(conn)
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