#coding=utf-8
#公众号
import tornado
import hashlib
from tornado.ioloop import IOLoop
from tornado import gen

class WeixiHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        get_class = self.get_argument('class', "0")
        get_class1 = self.get_argument('class1', "0")
        get_class2 = self.get_argument('class2', "0")
        get_class3 = self.get_argument('class3', "0")
        self.write(get_class)