#coding=utf-8
import tornado.web
import tornado.ioloop
import tornado.escape
from tornado.options import define, options
from tornado.httpserver import HTTPServer
import socket
from handlers.main.main_urls import handlers
from config import settings
from start import start_fu
from handlers.log.mylog import logInit
from handlers.log.tornado_log import log_request
from handlers.log.tornado_log import init_logging
import os

#定义一个默认的端口
define("port", default=8000, help="run port ", type=int)
# define("t",  default=False, help="creat tables", type=bool)
#
if __name__ == "__main__":
    # sockets = tornado.netutil.bind_sockets(9204)
    # task_id = tornado.process.fork_processes(2)
    # print(task_id)
    StartType = "bind_sockets" #listen,bind,bind_sockets
    Htype = False# 多进程开关
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    # print(log_path)

    # 设置语言环境和翻译文件位置
    locale_url = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "languages")
    tornado.locale.load_gettext_translations(locale_url, 'en_US')
    tornado.locale.set_default_locale('zh_CN')
    # 启动http服务
    # 解析命令行，进程端口优先
    options.parse_command_line()
    # 参数
    app = tornado.web.Application(handlers, **settings)
    app.settings["log_function"] = log_request
    # http_server = HTTPServer(app, xheaders=True)#http
    # import ssl
    # ssl_dir = os.path.abspath("/home/ssl/")
    # # ssl_ctx = {
    # #     "certfile": os.path.join(ssl_dir, "fullchain.pem"),
    # #     "keyfile": os.path.join(ssl_dir, "privkey.pem"),
    # # }
    # ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_ctx.load_cert_chain(os.path.join(ssl_dir, "fullchain.pem"),
    #                         os.path.join(ssl_dir, "privkey.pem"))
    if StartType == "listen":
        # 单线程
        http_server = HTTPServer(app, xheaders=True)
        http_server.listen(options.port)
        # init_logging("%s/log/syslog.log" % (os.path.dirname(os.path.abspath(__file__))))
        # tornado.ioloop.IOLoop.instance().start()
    elif StartType == "bind":
        # 简单多进程
        http_server = HTTPServer(app, xheaders=True)
        http_server.bind(options.port, family=socket.AF_INET)
        http_server.start(2)  # Forks multiple sub-processes
    elif StartType == "bind_sockets":
        # 高级多进程
        from tornado.netutil import bind_sockets
        if settings['IPV4_ONLY']:
            sockets = bind_sockets(options.port, family=socket.AF_INET)
        else:
            sockets = bind_sockets(options.port)
        if not settings['debug'] and Htype == True:
            import tornado.process
            tornado.process.fork_processes(0)# 0 表示按 CPU 数目创建相应数目的子进程
        server = HTTPServer(app, xheaders=True)
        server.add_sockets(sockets)
    logInit(log_path)
    start_fu()
    print('start server...')
    # tornado.ioloop.IOLoop.current().start()
    tornado.ioloop.IOLoop.instance().start()

