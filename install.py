# -*- coding: utf-8 -*-
from handlers.myredis.redis_class import RedisClass

R = RedisClass()
try:
    R.RH.set("server_ip", "103.86.46.13:9008")
    print("set ok.")
except:
    print("set error.")
exit()