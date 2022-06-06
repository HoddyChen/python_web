#coding:utf8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define,options

define("port",default=8000,help="run tornado service",type=int)

class IndexHandle(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

settings = {
    "debug": True,
    "template_path":"templates",
    "static_path":"static"
}
if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
        (r"/",IndexHandle)
    ],**settings)
    http_service = tornado.httpserver.HTTPServer(app)
    http_service.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()