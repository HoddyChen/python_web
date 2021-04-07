#coding=utf-8
#发送错误代码
import tornado
from tornado import gen
# from handlers.base.base_handler import BaseHandler
from datetime import datetime
from models.user.master_model import MasterModel
from models.user.sendmail_model import SendmailModel
from handlers.myredis.redis_class import RedisClass
from models.public.confrom_model import ErrorForm
from models.public.SendOrderError_model import OrderError
import re
import random
import hashlib
import config
import logging

logger = logging.getLogger('Main')
class SendOrderErrorHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        F = ErrorForm(self.request.arguments)
        if F.validate() and F.cla.data == "SendError":
            #交易失败发送提示
            ukid = F.ukid.data
            AccountNumber = F.f2.data
            md5_from = F.f5.data
            key_ma = F.f10.data
            ErrorNumber = F.f8.data
            Language = F.f7.data
            strtext = F.f9.data
            R = RedisClass()
            uaid = yield R.chick_MD5_uaid(str(AccountNumber), md5_from, ukid)
            followid = yield R.get_Mater_uaid(key_ma)
            if int(uaid) > 0 and followid != None:
                M = MasterModel()
                Master_data = yield M.getMasterEmail(followid)
                E = OrderError()
                err_text = E.getErrorText(ErrorNumber, Language)
                sendH = SendmailModel()
                tomail = []
                tomail.append(Master_data['email'])
                if Language == 0:
                    mail_text = ""#跟单账号提示：<BR>
                    mail_text = mail_text + err_text + "<BR>"
                    mail_text = mail_text + strtext + "<BR>"
                    mail_text = mail_text + "请人工检查跟单账号MT4的网络与交易平台是否正常运行.<BR>"
                    mail_text = mail_text + "-----来自[提示发送系统]<BR>"
                    mail_title = "跟单账号" + str(AccountNumber) + "的提示"
                else:
                    mail_text = "Documentary account message：<BR>"
                    mail_text = mail_text + err_text + "<BR>"
                    mail_text = mail_text + strtext + "<BR>"
                    mail_text = mail_text + "Please manually check if the MT4 network and Broker of the documentary account are running normally.<BR>"
                    mail_text = mail_text + "-----From [Prompt Sending System]<BR>"
                    mail_title = "Documentary account " + str(AccountNumber) + " message"
                send_flag = yield sendH.email_send(tomail, mail_text, mail_title)
                if send_flag == True:
                    url_text = "1,1,"
                else:
                    url_text = "0,0,"
            else:
                url_text = "0,0,"
        else:
            # 表单错误
            from models.public.confrom_model import get_ErrorForm
            echo = get_ErrorForm(F)
            logger.error("[SendOrderErrorHandler]:" + echo)
            url_text = "0,0,"

        self.write(url_text + config.StringEnd)
        self.finish()