#coding=utf-8
import tornado
from tornado import gen
from handlers.base.base_handler import BaseHandler
class IndexHandler(BaseHandler):
# class IndexHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        ip = ""
        # print(self.request.headers)
        ip = self.get_user_ip()
        ip1 = self.request.remote_ip
        ip2 = self.request.headers.get("X-Real-Ip", "")
        ip3 = self.request.headers.get("X-Forwarded-For", "")
        ip2 = str(ip1)+","+str(ip2)+","+str(ip3)
        # self.clear_cookie("current_strategy")
        yield self.render("index.html", ip=ip, ip2=ip2)

class ErrorHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        yield self.render("user/error.html")\

    @gen.coroutine
    def post(self):
        yield self.render("user/error.html")