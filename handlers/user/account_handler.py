#coding=utf-8
#交易账户视图
import tornado
import hashlib
import config
from models.user.user_model import UserModel
from tornado.ioloop import IOLoop
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.myredis.redis_class import RedisClass
import logging
import time

logger = logging.getLogger('Main')
# class AccountHandler(tornado.web.RequestHandler):
class AccountHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        start_time = time.time()
        get_class = self.get_argument('class')
        users = {
            "uname": self.get_argument('f0', ""),
            "ptname": self.get_argument('f1', "").replace(".", ""),
            "account": self.get_argument('f2', "0"),
            "allname": self.get_argument('f3', ""),
            "accountserver": self.get_argument('f4', ""),
            "md5_from": self.get_argument('f5', "0"),
            "Master_flag": self.get_argument('f6', "0"),
            "MasterKey": self.get_argument('f10', "0"),
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
            "minlot": self.get_argument('o14', "0"),
            "maxlot": self.get_argument('o15', "0"),
            "pid": self.get_argument('s0', "0"),
            "version": self.get_argument('s1', ""),
            "ukid": self.get_argument('ukid', "0"),
            "maxtime": self.get_argument('o21', "0"),#parameter01
            "maxloss": self.get_argument('o22', "0"),#parameter02
            "maxnum": self.get_argument('o23', "0"),
            "fixed": self.get_argument('o24', "0"),
            "percent": self.get_argument('o25', "0"),
            "rate_min": self.get_argument('o26', "0"),
            "rate_max": self.get_argument('o27', "0"),
            "reflex": self.get_argument('o28', "0"),
            "rate": self.get_argument('o29', "0"),# 先作预警风控线
            "allowed_sign": self.get_argument('o30', "0"),
            "tpsl_flag": self.get_argument('o31', "0"),# 止损止盈标志
            "parameter_time": self.get_argument('o99', "0"),
            "ip": self.get_user_ip(),
            "uid": 0,
        }
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
            users['get_class'] = get_class
            if get_class == "login":
                data_echo = yield y.GetAccount(users)#tornado.gen.Task
                # logger.info(self.get_arguments)
              # 执行Task函数，内部还是返回future对象。Task函数上第一个参数是要执行的函数，第二个是参数
            elif get_class == "check":
                data_echo = yield y.CheckAccount(users)
            elif get_class == "exit":
                data_echo = yield y.ExitAccount(users)
            # print(data_echo)
            self.write(data_echo + config.StringEnd)
        else:
            self.write('-5,0,0,0,0,0,0,0,0,' + config.StringEnd)
        count_time = (time.time()-start_time)*1000
        logger.info("run_time:%s ms" % str(count_time))
        self.finish()

