#coding=utf-8
#发送验证码
import tornado
from tornado import gen
from models.user.sendmail_model import SendmailModel
from handlers.myredis.redis_class import RedisClass
import random
import config
import logging
from models.public.confrom_model import SendEmailForm
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.user.master_model import MasterModel
import json

logger = logging.getLogger('Main')
class SendmailHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def post(self):
        F = SendEmailForm(self.request.arguments)
        echo_dist = {}
        if F.validate():#and F.cla.data == "SendError"
            if tornado.escape.to_unicode(self.request.arguments['_xsrf'][0]) != self.session['_xsrf']:
                echo_dist['echo'] = "验证失败"
                echo_dist['reponse_status'] = 1
            else:
                #邮箱验证成功
                R = RedisClass()
                sendH = SendmailModel()
                M = MasterModel()
                m_data = yield M.checkMaterMail(F.umail.data)
                logger.debug(m_data)
                if len(m_data) == 0:
                    # 策略邮箱不存在
                    echo_dist['reponse_status'] = 4
                else:
                    # mail_key = str(random.randint(100000, 999999))
                    mail_key = "".join(random.sample('123567890', 6))
                    mail_text = self.locale.translate("跟单系统登陆验证码")
                    mail_text = mail_text + """：
                    
                    """
                    mail_text = mail_text + mail_key
                    mail_text = mail_text + """
                    
                    """
                    mail_text = mail_text + self.locale.translate("请不要将验证码转发或给其他人查看")
                    mail_text = mail_text + """！！！！！
                    
                    -----"""
                    mail_text = mail_text + self.locale.translate("来自[跟单交易多账户管理系统]")
                    tomail = []
                    tomail.append(F.umail.data)
                    send_flag = yield sendH.email_send(tomail, mail_text, self.locale.translate("主策略账号登陆验证码"))
                    if send_flag == True:
                        R.RH.set(config.redis_session_uaid_set + str(F.umail.data), mail_key, ex=config.SessionsOutTime)
                        echo_dist['reponse_status'] = 5 #  发送成功
                    else:
                        echo_dist['reponse_status'] = 2 # 发送失败
        else:
            # 表单错误
            from models.public.confrom_model import get_ErrorForm
            echo_dist['echo'] = get_ErrorForm(F)
            echo_dist['reponse_status'] = 0 # 输入错误

        self.write(json.dumps(echo_dist))
        self.finish()

