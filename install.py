# -*- coding: utf-8 -*-
from handlers.myredis.redis_class import RedisClass

R = RedisClass()
try:
    # R.RH.set("server_ip", "64.31.63.252:9008")
    # print("server_ip:", R.RH.get("server_ip"))
    print("server_ip:", R.get_socket_sercerIP())
    # print("set ok.")
except:
    print("set error.")
exit()