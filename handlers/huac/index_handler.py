#coding=utf-8
#公众号
import tornado
import hashlib
from tornado.ioloop import IOLoop
from tornado import gen

class IndexHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        pass