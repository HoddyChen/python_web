#coding=utf-8
# 验证码
import tornado
from tornado import gen
import requests

class Recaptcha_Handler(tornado.web.RequestHandler):

    @gen.coroutine
    def post(self):
        url = 'https://recaptcha.net/recaptcha/api/siteverify'
        # key = "6Le_FL8UAAAAAOnkBVOwiIqO6Dm09lCjXSnrQ6Qr"
        key = "6LeU8KMUAAAAALDrNrgYEhYmmOzw2EbgzAs3dlLk"
        # 验证码
        token = self.get_argument('token', 0)
        # 用户输入
        # response = self.get_argument('recaptcha_response_field')
        data = {
            'secret': key,
            'response': token,
            'remoteip': self.request.remote_ip,
        }
        response = requests.post(url, data=data)
        # res = urlopen(url, data=urlencode(data).encode())
        # 获取验证结果，这里直接将返回结果输出到页面
        yield self.write(response.text)
        self.finish()