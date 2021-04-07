#coding=utf-8
#发送验证码
import tornado
from tornado import gen
# from handlers.base.base_handler import BaseHandler
from datetime import datetime
from models.user.user_model import UserModel
from models.user.sendmail_model import SendmailModel
from handlers.myredis.redis_class import RedisClass
import re
import random
import hashlib
import config
import logging

logger = logging.getLogger('Main')
class SendmailHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        get_class = self.get_argument('class')
        ukid = self.get_argument('ukid')
        AccountNumber = self.get_argument('f2')
        md5_from = self.get_argument('f5')
        umail = self.get_argument('f11', "")
        par = r'^[\.a-zA-Z0-9_\-]{1,30}@[a-zA-Z0-9_\-]+\.([a-zA-Z0-9_\-]{1,5})$'
        if re.match(par, umail):
            #邮箱验证成功
            R = RedisClass()
            uaid = yield R.chick_MD5_uaid(AccountNumber, md5_from, ukid)
            # print(uaid)
            if uaid > 0:
                sendH = SendmailModel()
                # mail_key = str(random.randint(100000, 999999))
                mail_key = "".join(random.sample('123567890', 6))
                mail_text = """主策略账号登陆验证码：
                
                """
                mail_text = mail_text + mail_key
                mail_text = mail_text + """
                
                请不要将验证码转发或给其他人查看！！！！！
                -----来自[跟单交易多账户管理系统]"""
                tomail = []
                tomail.append(umail)
                send_flag = yield sendH.email_send(tomail, mail_text, "主策略账号登陆验证码")
                if send_flag == True:
                    md5_str = mail_key + AccountNumber + str(config.TineMd5Info)
                    str_md5 = hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()
                    R.RH.set(config.redis_session_uaid_set + str(uaid), mail_key, ex=config.SessionsOutTime)
                    url_text = "1," + str_md5 + ","
                else:
                    url_text = "0,-1,"
            else:
                url_text = "0,-2,"
        else:
            url_text = "0,-3,"

        self.write(url_text + config.StringEnd)
        self.finish()

