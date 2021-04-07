# coding = utf-8
import logging
import os
from tornado import ioloop, gen
from tornado.tcpclient import TCPClient
from handlers.log.mylog import logInit_socket_client
from socket_client.models.socket_client_model import SocketClientModel
import config

def main():
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    logInit_socket_client(log_path)
    client_id = 0
    c1 = SocketClientModel(config.server_list[client_id]['url'], config.server_list[client_id]['port'],client_id)
    c1.start()
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()