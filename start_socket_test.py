# coding=utf-8
from tornado import ioloop, gen, iostream
from handlers.copy_socket.socket_handler import CopyServer
import os
import ssl
from handlers.log.mylog import logInit_socket
import tornado
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream, SSLIOStream
# from tornado.netutil import bind_sockets, add_accept_handler, ssl_wrap_socket
# from tornado import process
# from tornado.util import errno_from_exception

if __name__ == '__main__':
    print("TCPServer start ......")
    # ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_ctx.load_cert_chain(os.path.join("/home/ssl/", "fullchain.pem"),
    #                         os.path.join("/home/ssl/", "privkey.pem"))
    # TCPServer(ssl_options=ssl_ctx)
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    logInit_socket(log_path)
    # server = CopyServer(ssl_options=ssl_ctx)
    server = CopyServer()
    server.listen(9000)
    # server.bind(9000)# Forks multiple sub-processes
    # server.start(0)  # Forks multiple sub-processes
    ioloop.IOLoop.current().start()
    # 3.
    # `add_sockets`: advanced
    # multi - process::
    #
    # sockets = bind_sockets(9000)
    # tornado.process.fork_processes(0)
    # server = TCPServer()
    # server.add_sockets(sockets)
    # IOLoop.current().start()
