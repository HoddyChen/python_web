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

R = RedisClass()
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
logInit_socket_robot_client(log_path)
logger = logging.getLogger('robot_clinet')

client_id = 1

def main():


    # R.ResetTotalConsole()
    logger.info("start_client......%s" % client_id)

def chick_redisConsole():
    # print("2")
    try:
        # TotalConsoleDist = R.pop_TotalConsole(client_id)
        TotalConsoleDist = R.pop_Console_list(client_id)
        if TotalConsoleDist != {}:
            # 发送命令
            # logger.debug("Time:%s,%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),TotalConsoleDist))
            send_client(TotalConsoleDist)
    except Exception as e:
        logger.error("err:%s" % e)

def send_client(TotalConsoleDist):
    client_ioloop = ioloop.IOLoop.instance()
    # client_ioloop = ioloop.IOLoop.current()
    c1 = SocketClientModel(logger, client_id, client_ioloop)
    c1.start(TotalConsoleDist)
    client_ioloop.start()

if __name__ == '__main__':
    main()
    while True:
        chick_redisConsole()
        time.sleep(0.005)