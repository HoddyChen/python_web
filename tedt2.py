import config
import time
from tornado import ioloop, gen, iostream
# import datetime
# import tormysql
# import pymysql
# from tornado import gen

from handlers.myredis.redis_class import RedisClass

from models.public.headers_model import global_Models
import config
from models.my_socket.my_socket_model import MySocketModel
# def main():
#     # from models.user.order_model import OrderModel
#     # O = OrderModel()
#     # order_num = yield O.get_PositionOrderNum(4490)
#     # S = MySocketModel()
#     # pp = yield S.get_chick_orders2(4495, "089bb6b18604cda2fd8611e085a289c8")
#     print("11")
# if __name__ == '__main__':
#     main()yy = R.RH.hget(config.redis_acount_md5_dic, "449a5dc904bef5315828a0d3ee7dd857")
#getCopyText:{"type":"copyorder","ukid":"449a5dc904bef5315828a0d3ee7dd857","f2":"861649","f5":"e94fe0343a3e495b740419d83343bd2d","f10":""}

R = RedisClass()
yy = R.chick_MD5_uaid("861649", "e94fe0343a3e495b740419d83343bd2d", "449a5dc904bef5315828a0d3ee7dd857")
print(yy)
