# coding = utf-8
import logging
import os
from tornado import ioloop, gen
from tornado.tcpclient import TCPClient
from handlers.log.mylog import logInit_socket_robot_client
from socket_client.models.socket_client_model import SocketClientModel
import config
import time
from handlers.myredis.redis_class import RedisClass

client_id = 1
R = RedisClass()
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
logInit_socket_robot_client(log_path)
logger = logging.getLogger('robot_client')
def main():

    R.ResetTotalConsole()
    print("start_client......", client_id)

def chick_redisConsole():
    # print("2")
    try:
        # print(config.server_list[client_id]['url'], config.server_list[client_id]['port'])
        # R = RedisClass()
        # TotalConsoleDist = R.pop_TotalConsole(client_id)
        TotalConsoleDist = R.pop_Console_list(client_id)
        if TotalConsoleDist:
            # 发送命令
            print("Time:%s,%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),TotalConsoleDist))
            send_client(TotalConsoleDist)
    except Exception as e:
        print("err:", e)

def send_client(TotalConsoleDist):
    client_ioloop = ioloop.IOLoop.instance()
    c1 = SocketClientModel(client_id, client_ioloop)
    c1.start(TotalConsoleDist)
    client_ioloop.start()

if __name__ == '__main__':
    main()
    while True:
        chick_redisConsole()
        time.sleep(0.002)