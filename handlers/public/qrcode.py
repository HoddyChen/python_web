#coding=utf-8
# 二维码生成
import tornado
import hashlib
from tornado.ioloop import IOLoop
from tornado import gen
from models.public.qrcode_model import qc

class QrCode_Handler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        reid = self.get_argument('reid', 0)
        wechat_id = self.get_argument('wechat_id', 0)
        info = {}
        info['url'] = "http://%s/weixi/index?reid=%s&wechat_id=%s" % (self.request.host, str(reid), str(wechat_id))
        yield self.write(qc(info))
        self.finish()