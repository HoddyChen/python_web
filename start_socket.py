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
def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

if __name__ == '__main__':
    import socket
    ip = get_host_ip()
    iplist = ip.split(".")
    client_label = iplist[3]
    port = 9000
    print(str(ip))
    print("TCPServer start ......")
    from models.public.headers_model import global_Models
    G = global_Models()
    G.set_map("ServerTime", 0)
    # ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_ctx.load_cert_chain(os.path.join("/home/ssl/", "fullchain.pem"),
    #                         os.path.join("/home/ssl/", "privkey.pem"))
    # TCPServer(ssl_options=ssl_ctx)

    from handlers.myredis.redis_class import RedisClass
    R = RedisClass()
    R.register_socketIP(ip, port, client_label)
    # R.register_socketIP(socket.gethostbyname(socket.gethostname()), port, client_label)
    # R.register_socketIP("127.0.0.1", port, client_label)
    del R
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    logInit_socket(log_path)
    # server = CopyServer(ssl_options=ssl_ctx)
    server = CopyServer()
    server.listen(port)
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