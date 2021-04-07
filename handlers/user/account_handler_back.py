#coding=utf-8
#交易账户视图
import tornado
import hashlib
import config
from models.user.user_model import UserModel
from tornado.ioloop import IOLoop
from tornado import gen
from handlers.myredis.redis_class import RedisClass
import logging

logger = logging.getLogger('Main')
class AccountHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        get_class = self.get_argument('class')
        users = {
            "uname": self.get_argument('f0', ""),
            "ptname": self.get_argument('f1', "").replace(".", ""),
            "account": self.get_argument('f2', "0"),
            "allname": self.get_argument('f3', ""),
            "accountserver": self.get_argument('f4', ""),
            "md5_from": self.get_argument('f5', "0"),
            "Master_flag": self.get_argument('f6', "0"),
            "balance": self.get_argument('o1', "0"),
            "credit": self.get_argument('o2', "0"),
            "quity": self.get_argument('o3', "0"),
            "profit": self.get_argument('o4', "0"),
            "margin": self.get_argument('o5', "0"),
            "xs": self.get_argument('o6', "0"),
            "ea": self.get_argument('o7', "0"),
            "moni": self.get_argument('o8', "0"),
            "gangan": self.get_argument('o9', "0"),
            "huobi": self.get_argument('o10', "0"),
            "huibimodel": self.get_argument('o11', "0"),
            "stopoutlevel": self.get_argument('o12', "0"),
            "stopoutmode": self.get_argument('o13', "0"),
            "pid": self.get_argument('s0', "0"),
            "version": self.get_argument('s1', ""),
            "ukid": self.get_argument('ukid', "0"),
            "parameter01": self.get_argument('o21', "0"),
            "parameter02": self.get_argument('o22', "0"),
            "parameter03": self.get_argument('o23', "0"),
            "parameter04": self.get_argument('o24', "0"),
            "parameter05": self.get_argument('o25', "0"),
            "parameter06": self.get_argument('o26', "0"),
            "parameter07": self.get_argument('o27', "0"),
            "parameter08": self.get_argument('o28', "0"),
            "parameter09": self.get_argument('o29', "0"),
            "parameter10": self.get_argument('o30', "0"),
            "parameter_time": self.get_argument('o99', "0"),
        }
        #print(users)
        #整理数据
        if users['ea'] =="true" or users['ea'] == "1":
            users['ea'] == 1
        else:
            users['ea'] == 0
        if users['moni'] == "true":
            users['moni'] == 1
        else:
            users['moni'] == 0
        #
        md5_str = users['account'] + users['version']
        str_md5 = hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()
        # 验证
        #datas = ""
        y = UserModel()
        if users['md5_from'] == str_md5:
            if get_class == "login":
                data_echo = yield y.GetAccount(users)#tornado.gen.Task
                logger.info(self.get_arguments)
              # 执行Task函数，内部还是返回future对象。Task函数上第一个参数是要执行的函数，第二个是参数
            elif get_class == "check":
                data_echo = yield y.CheckAccount(users)
            elif get_class == "exit":
                data_echo = yield y.ExitAccount(users)
            # print(data_echo)
            self.write(data_echo + config.StringEnd)
        else:
            self.write('-1,0,0,0,0,0,0,0,0,' + config.StringEnd)
        self.finish()

