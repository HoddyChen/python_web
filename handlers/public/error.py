#coding=utf-8
#错误
import tornado
import hashlib
from tornado.ioloop import IOLoop
from tornado import gen
from handlers.session.session_handler import SessionHandler
from models.public.headers_model import Headers_Models
from handlers.base.base_handler import BaseHandler

class ErrorHandler(SessionHandler, tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        # self.session['face_img'] = "face.png"
        # page_main = {}
        # page_main['title'] = "NetCon Home"
        # if self.session['uid'] == None:
        #     page_main['title'] = "++" + page_main['title']
        # else:
        #     page_main['title'] = "*" + str(self.session['uid']) + "*" + page_main['title']

        # 根据用户硬件类型返回模板
        # H = Headers_Models()
        # header_flag = yield H.chick_Mobile(self.request, self.session['uid'], self.session['temp_uid'])
        # if header_flag == True:
        #     # 手机模板
        #     yield self.render("web/error.html", session=self.session)
        # else:
            # 电脑模板
        yield self.render("user/error.html")