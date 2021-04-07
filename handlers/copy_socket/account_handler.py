#coding=utf-8
#交易账户视图
import hashlib
from models.user.user_model import UserModel
from tornado.ioloop import IOLoop
from tornado import gen
from handlers.myredis.redis_class import RedisClass

class AccountHandler:

    @staticmethod
    @gen.coroutine
    def get(msg_dict):
        get_class = msg_dict['class']
        users = {
            "uname": msg_dict.get('f0'),
            "ptname": msg_dict.get('f1').replace(".", ""),
            "account": msg_dict.get('f2'),
            "allname": msg_dict.get('f3'),
            "accountserver": msg_dict.get('f4'),
            "md5_from": msg_dict.get('f5'),
            "Master_flag": msg_dict.get('f6'),
            "balance": msg_dict.get('o1'),
            "credit": msg_dict.get('o2'),
            "quity": msg_dict.get('o3'),
            "profit": msg_dict.get('o4'),
            "margin": msg_dict.get('o5'),
            "xs": msg_dict.get('o6'),
            "ea": msg_dict.get('o7'),
            "moni": msg_dict.get('o8'),
            "gangan": msg_dict.get('o9'),
            "huobi": msg_dict.get('o10'),
            "huibimodel": msg_dict.get('o11'),
            "stopoutlevel": msg_dict.get('o12'),
            "stopoutmode": msg_dict.get('o13'),
            "pid": msg_dict.get('s0'),
            "version": msg_dict.get('s1'),
            "ukid": msg_dict.get('ukid'),
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
              # 执行Task函数，内部还是返回future对象。Task函数上第一个参数是要执行的函数，第二个是参数
            elif get_class == "check":
                data_echo = yield y.CheckAccount(users)
            elif get_class == "exit":
                data_echo = yield y.ExitAccount(users)
            print(data_echo)
            return data_echo
        else:
            return '-1,0,0,0,0,0,0,0,0,'