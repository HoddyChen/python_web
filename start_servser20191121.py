#coding=utf-8
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.escape
from tornado.options import define, options
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
logger = logInit()
if __name__ == "__main__":
    # sockets = tornado.netutil.bind_sockets(9204)
    # task_id = tornado.process.fork_processes(2)
    # print(task_id)
    start_fu()
    # 启动http服务
    options.parse_command_line()
    app = tornado.web.Application(handlers, **settings)
    app.settings["log_function"] = log_request
    # http_server = tornado.httpserver.HTTPServer(app)#http
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)#https,
    #http_server.listen(8037)#options.port
    http_server.listen(options.port)
    # http_server.start(0)  # forks one process per cpu
    print('start server...')
    init_logging("%s/log/syslog.log" % (os.path.dirname(os.path.abspath(__file__))))
    tornado.ioloop.IOLoop.instance().start()

    # server = HTTPServer(application)
    # server.bind(8888)
    # server.start(4)  # Forks multiple sub-processes
    # tornado.ioloop.IOLoop.current().start()
