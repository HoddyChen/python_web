#coding=utf-8
from hashlib import sha1
import os
import time
import config
# from hash_ring import HashRing
from handlers.myredis.redis_class import RedisClass

# # 缓存服务器列表
# cache_servers = [
#     '192.168.0.246:11212',
#     '192.168.0.247:11212',
#     '192.168.0.249:11212'
# ]
#
# # 配置权重
# weights = {
#     '192.168.0.246:11212': 2,
#     '192.168.0.247:11212': 2,
#     '192.168.0.249:11212': 1
# }

# ring = HashRing(cache_servers, weights)# 实例化HashRing对象

# 随机生成session_id
create_session_id = lambda: sha1(bytes('%s%s' % (os.urandom(16), time.time()), encoding='utf-8')).hexdigest()

class Session:
    """自定义session"""

    # info_container = {
    #     # session_id: {'user': info} --> 通过session保存用户信息，权限等
    # }

    def __init__(self, handler):
        """
        初始化时传入RequestHandler对象，通过它进行cookie操作
        self.handler.set_cookie()
        self.handler.get_cookie()
        :param handler:
        """
        self.handler = handler
        self.R = RedisClass()
        # 从 cookie 中获取作为 session_id 的随机字符串，如果没有或不匹配则生成 session_id
        random_str = self.handler.get_secure_cookie('session_id')
        if (not random_str) or (not self.R.RH.exists(random_str)):
            random_str = create_session_id()
            self.R.RH.hset(random_str, "temp_uid", random_str)
        self.R.RH.expire(random_str, config.SessionsOutTime)
            # self.info_container[random_str] = {}
        self.random_str = random_str

        # 每次请求进来都会执行set_cookie，保证每次重置过期时间为当前时间以后xx秒以后
        self.handler.set_secure_cookie('session_id', random_str, max_age=config.SessionsOutTime)
        # self.handler.set_secure_cookie('session_id', random_str, expires_day=None)

        # print(random_str)

    def __getitem__(self, item):
        # get_node()根据随机字符串哈希取模的结果，来选取服务器；再通过split方式提取服务器hotst和port
        # host, port = ring.get_node(self.random_str).split(':')
        # conn = redis.Redis(host=host, port=port)
        return self.R.RH.hget(self.random_str, item)

    def __setitem__(self, key, value):
        # host, port = ring.get_node(self.random_str).split(':')
        # conn = redis.Redis(host=host, port=port)
        if value == None:
            value = ""
        self.R.RH.hset(self.random_str, key, value)

    def __delitem__(self, key):
        # host, port = ring.get_node(self.random_str).split(':')
        # conn = redis.Redis(host=host, port=port)
        self.R.RH.hdel(self.random_str, key)

    def delete(self):
        """从大字典删除session_id"""
        # del self.info_container[self.random_str]
        self.R.RH.delete(self.random_str)

class SessionHandler:
    def initialize(self):
        self.session = Session(self)  # handler增加session属性
        # print("123")

    def add_AdminSession(self, adminInfo):
        self.session['adminid'] = adminInfo['adminid']
        self.session['uid'] = adminInfo['uid']
        self.session['admin_name'] = adminInfo['admin_name']
        self.session['admin_face_img'] = adminInfo['admin_face_img']
        self.session['face_img'] = adminInfo['face_img']
        self.session['uname'] = adminInfo['uname']
        self.session['position_name'] = adminInfo['position_name']
        self.session['department_name'] = adminInfo['department_name']
        return

    def add_UserSession(self, userInfo):
        self.session['uid'] = userInfo['uid']
        self.session['uname'] = userInfo['uname']
        self.session['face_img'] = userInfo['face_img']
        return

#* 调用：类继承SessionHandler
# 操作session：
# 通过self.session[key] = value 即可调用session对象的__setitem__方法来写session；
# 通过self.session[key] 即可调用session对象的__getitem__方法来获取session
# 通过del self.session[key] 即可调用session对象的__delitem__方法来删除session
# 通过self.session.delete()，即可调用session对象的delete方法，删除整个session_id


