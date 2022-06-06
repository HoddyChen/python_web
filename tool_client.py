# coding = utf-8
from handlers.myredis.redis_class import RedisClass
import config

R = RedisClass()
# 命令总数（余下）
num = R.RH.llen(config.redis_total_console_list)
print("命令总数: %s " % str(num))#
# kkk = R.RH.lpop(config.redis_total_console_list)
# kkk = R.RH.llen(config.redis_total_console_list)
# kkk = R.RH.lindex(config.redis_total_console_list, 0)
# R.RH.delete(config.redis_total_console_list)
# kkk = R.RH.llen(config.redis_total_console_list)
# print(kkk)

# 删除命令con_id，flag_
# pp = R.RH.keys("con_id*")
# for p1 in pp:
#     R.RH.delete(p1)
#     print(p1)
# print("总删除：%s" % len(pp))
# R.RH.delete(config.redis_total_console_list)