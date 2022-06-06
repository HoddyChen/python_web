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
from models.public.headers_model import DistMD5
from models.public.headers_model import global_Models
import socket
import json
import threading

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
logInit_socket_client(log_path)
logger = logging.getLogger('Client')
client_id = 999
R = RedisClass()
G = global_Models()

def read_chat(stream):  # 谁发送的、发送的内容
    """
    读取别人发送过来的数据
    :param socket:
    :return:
    """
    while True:
        try:
            msg = stream.client.recv(1024).decode()
            # msg = yield stream.read_until(bytes("\n", encoding="utf8"))
            if msg != "":
                msg = msg[:-6]
                logger.debug("[SocketClientModel:read_chat]read:%s" % msg)

            # 将接收到的信息、打印到控制台上
            print("msg:%s" % msg)
        except ConnectionResetError:
            print("read:服务器连接失败、请重新连接~")
            a = socketClient(stream.client, stream.label, stream.host, stream.port)
            a.chat({})


def write_chat(stream):  # 谁发的、发给谁的、内容
    """
    发送信息给to_qq
    :param socket:
    :param to_qq:
    :return:
    """
    while True:
        # msg = input()
        # 准备发送给服务器的内容
        # msg = f"{to_qq}:{msg}"
        # 将信息发送给服务器
        try:
            # socket.send(msg.encode())
            msg_str = chick_redisConsole(stream.label)
            if msg_str:
                # 发送数据
                # time_vol = int(time.time())
                stream.client.send(msg_str)
                G.set_map("time_vol_" + stream.label, int(time.time()))
                print("write:%s" % msg_str)
        except ConnectionResetError:
            print("write:服务器连接失败、请重新连接~")
            # break
            a = socketClient(stream.client, stream.label, stream.host, stream.port)
            a.chat({})

def chick_redisConsole(label):
    msgDist = R.pop_Console_list()
    if not msgDist:
        if time.time() - int(G.get("time_vol_" + label)) < 1*55:
            return None
    if msgDist == {}:
        msgDist["sendid"] = 0
        msgDist["followid"] = 0
        msgDist["fx_type"] = "ChickStatus"
    msgDist['label'] = client_id
    msgDist['key2'] = config.ServerMd5Info
    msgDist['key'] = DistMD5.encryptDist(msgDist)
    msg_str = bytes(json.dumps(msgDist) + "\n", encoding="utf8")
    return msg_str

class socketClient:
    """
        QQ Client
    """

    def __init__(self, client_id, label, host, port):
        """
        初始化QQ号、并建立链接
        :param qq:
        """
        self.client_id = client_id
        self.label = label
        self.host = host
        self.port = port
        # 创建 socket 客户端
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接服务器
        self.client.connect((host, int(port)))
        # 发送自己的身份，给服务器
        # self.client.send(self.qq.encode())
        G.set_map("time_vol_" + label, 0)

    def chat(self, to_qq):
        """
        和谁聊天
        :param to_qq:
        :return:
        """
        # 开启两个线程、分别进行接收(读取)数据、和发送(写入)数据
        threading.Thread(target=read_chat, args=(self,)).start()
        threading.Thread(target=write_chat, args=(self,)).start()

def main():
    R = RedisClass()
    server_list = R.get_socket_sercerIP()
    # print("start_client......", client_id)
    # print(server_list)
    # i = 1
    a = {}
    for i in range(len(server_list)):
        print("start_client......%s" % server_list[i])
        a[server_list[i]['label']] = socketClient(client_id, server_list[i]['label'], server_list[i]['host'], server_list[i]['port'])
        a[server_list[i]['label']].chat({})
    # R.ResetTotalConsole()
    # print("start_client......", client_id)



if __name__ == '__main__':
    main()