#coding=utf-8
#验证验证码
import tornado
from tornado import gen
# from handlers.base.base_handler import BaseHandler
from datetime import datetime
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel
import re
import random
import hashlib
import config

class VcmailHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        get_class = self.get_argument('class')
        ukid = self.get_argument('ukid')
        AccountNumber = self.get_argument('f2')
        md5_from = self.get_argument('f5')
        umail = self.get_argument('f11', "")
        Ckey = self.get_argument('f12', "")
        pid = self.get_argument('s0', "0")

        par = r'^[\.a-zA-Z0-9_\-]{1,30}@[a-zA-Z0-9_\-]+\.([a-zA-Z0-9_\-]{1,5})$'
        echotext = ""
        if re.match(par, umail):
            #邮箱验证成功
            R = RedisClass()
            uaid = yield R.chick_MD5_uaid(AccountNumber, md5_from, ukid)
            if uaid > 0:
                mail_key = R.RH.get(config.redis_session_uaid_set + str(uaid))
                if mail_key == Ckey:
                    #验证成功
                    M = MasterModel()
                    #检查email账号注册并登陆
                    key_ma = yield M.getVcmial(umail, uaid)
                    if key_ma != None:
                        # 提取跟单的账号列表
                        yield R.insert_master_uaid(key_ma, uaid)
                        datas = yield M.getMaterFollow(uaid)
                        echotext2 = yield R.getRedisMaterFollow(datas)
                        maxnum = yield M.getMaterCopyNum(config.PID, uaid)
                        echotext = echotext + str(maxnum) + "_" + str(config.ERROR_TIME) + "," + key_ma + "," + echotext2
                    else:
                        echotext = "-2,0,"
                else:
                    echotext = "-3,0,"
            else:
                echotext = "-4,0,"
        else:
            echotext = "-5,0,"
        self.write(echotext + config.StringEnd)
        self.finish()
