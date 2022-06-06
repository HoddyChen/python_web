import config
import time
from tornado import ioloop, gen, iostream
# import datetime
# import tormysql
# import pymysql
# from tornado import gen
import re
# par4 = "?!(.*de)$"
par4 = ".*\.(com|cn|net|org|gov|edu|top)$"
# vol4 = re.compile(par4).findall("9900@gmailcn")
vol4 = re.match(par4, "9900@gmail.cn")
print(vol4)
# print(time.time())
# time.sleep(1)
#
exit()
from handlers.myredis.redis_class import RedisClass
# print(data)
# import os
# import random
# import re
# import hashlib
#
# class Record:
#     #定义两个类变量
#     item = {}
#     date = '2019-07-23'
#     def info(self):
#         self.item['oo'] = "pp"
#         print('info方法：',self.item)
#         print('info方法：',self.date)
# # rc = Record()
# # rc.info()
# pp = set()
# Record.item2 = "rr"
# print(Record.item2)
# exit()
# print(rc.date)
# rc.item['oo'] = "键盘"
# oo = {}
# # oo['ii'] = 0
# if not oo.get("ii") or 1-oo['ii'] > 0:
#     print("YY")
# else:
#     print("NN")
# # print(Record.item)
# rr = Record()
# print(rr.item)
# a="""
# \xe6\x97\xa5\xe5\x86\x85\xe4\xba\xa4\xe6\x98\x93,\xe7\xbe\x8e\xe8\x82\xa1\xe4\xba\xa4\xe6\x98\x93\xe8\xa7\x84\xe5\x88\x99,\xe7\xbe\x8e\xe8\x82\xa1\xe6\x9c\x80\xe5\xb0\x8f\xe4\xba\xa4\xe6\x98\x93\xe5\x8d\x95\xe4\xbd\x8d,\xe7\xbe\x8e\xe8\x82\xa1\xe7\x8e\xb0\xe9\x87\x91\xe8\xb4\xa6\xe6\x88\xb7,\xe7\xbe\x8e\xe8\x82\xa1\xe4\xbf\x9d\xe8\xaf\x81\xe9\x87\x91\xe8\xb4\xa6\xe6\x88\xb7,T+0\xe4\xba\xa4\xe6\x98\x93"""
# print(a.encode('raw_unicode_escape').decode('utf-8'))
# exit()
# ii = {"qq":[{"d":0,"p":9},{"d":0,"p":9}],"pp":9}
# if "pp" in ii:
#     print("1")
# else:
#     print("0")
# exit()
# os.system("python ./mo_tool/msgfmt.py -o ./mo_tool/en_US.mo ./mo_tool/en_US.po")
# os.system("python msgfmt.py -o en_US.mo en_US.po")
# pp = ["ii",'99']
# if "99" in pp:
#     pp.append("fxcns")
# print(pp.remove(3))
# exit()
# strComment = "from 63829971"
# par = "([0-9].+)"
# arr1 = re.compile(par).findall(strComment)
# print(time.time()-10)
# password_md5 = hashlib.md5("2204SN48".encode(encoding='UTF-8')).hexdigest()
# print(password_md5)
# exit()
#"ukid":"71a76f0e7a6a6e2e3fd48ab15b45fd33","f2":"861649","f5":"e94fe0343a3e495b740419d83343bd2d",
R = RedisClass()
yy = R.chick_MD5_uaid("861649", "e94fe0343a3e495b740419d83343bd2d", "71a76f0e7a6a6e2e3fd48ab15b45fd33")
print(yy)
exit()
# R.RH.set("jj4264", 0)
# print(R.RH.get("jj4264"))
# exit()
# from models.public.headers_model import global_Models
# import config
# from models.my_socket.my_socket_model import MySocketModel
# import datetime
# now = datetime.datetime.now()
# today = datetime.date.today()
# print(now - datetime.timedelta(days=now.weekday() + 7))
# print(int(time.mktime((today - datetime.timedelta(days=today.weekday() - 7)).timetuple())))
# exit()
# def main():
#     from models.user.order_model import OrderModel
#     O = OrderModel()
#     order_num = yield O.get_PositionOrderNum(4490)
#
#     # S = MySocketModel()
#     # pp = yield S.get_chick_orders2(4495, "089bb6b18604cda2fd8611e085a289c8")
#     print(order_num)
# if __name__ == '__main__':
#     main()
# print(R.RH.get(config.redis_ua_pid_endtime + "4264"))
# print(R.RH.hget(config.redis_master_uaid_Hash + "4264", "4361"))
# print(R.RH.hexists(config.redis_master_uaid_Hash + "4264", "4361"))
# a = time.time()
# R.get_socket_sercerIP()
# print(R.RH.get("server_ip"))
R.RH.set("server_ip", "103.86.46.13:9008")
# print(R.get_socket_sercerIP())
# # config.redis_total_console_list
# print(R.RH.llen("Console_list0"))
# # print(R.RH.lindex("Console_list0",0))
# # print(R.RH.hgetall(R.RH.lindex("Console_list0",0)))
# print(R.RH.llen("Console_list1"))
# print(R.RH.lindex("Console_list1",0))
# con_id = R.RH.lpop("Console_list1")
# print(R.RH.hgetall(con_id))
# print(R.RH.hgetall("96793989.91918747"))
exit()
# i = R.RH.get("sss333192168508399909000")
# R.RH.rpush("Console_list", "sss333192168508399909000")
# R.RH.lpop("Console_list")
# print(R.RH.hgetall("ouo"))
# R.RH.delete("ouo")
# from models.user.command_model import CommcandModel
# c = CommcandModel()
#
# c.setNewMarginCommcand(0, 0, "MakeUpOrder")
# print(R.pop_Console_list())

# print(R.RH.smembers("socket_server_set"))
G = global_Models()
# par = r'^\+?[1-9][0-9]*$'
par = r'^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$'
# import re
# host = "192.168.68.47"
# if re.match(par, host):
#     print("1")
# else:
#     print("2")
# print(R.get_socket_sercerIP())
import config
qq = R.pop_TotalConsole(1)
print(qq)#
kkk = R.RH.lpop(config.redis_total_console_list)
# kkk = R.RH.llen(config.redis_total_console_list)
# kkk = R.RH.lindex(config.redis_total_console_list, 0)
# R.RH.delete(config.redis_total_console_list)
# kkk = R.RH.llen(config.redis_total_console_list)
print(kkk)
pp = R.RH.keys("con_id*")
for p1 in pp:
    R.RH.delete(p1)
    print(p1)
print(len(pp))
# qq = R.RH.get("server_ip")

# it = time.time()
# p=[]
# class MySocketModel(RedisClass):
#
#     def __init__(self):
#         RedisClass.__init__(self)
#         self.msg_disc = {
#             'uaid': 0
#         }
#
#     # def __del__(self):
#     #     RedisClass.__del__(self)
# M = MySocketModel()
# M = None
# for i in R.RH.smembers("socket_server_set"):
#     print(i)
#     print(R.RH.hgetall(i))
#     k = G.set_map(i, R.RH.hgetall(i))
#     R.RH.delete(i)
# #     # p.append(R.RH.hgetall(i))
# R.RH.delete("socket_server_set")
# while True:
#     time.sleep(10)
# M = MySocketModel()
exit()
# G.set_map("socket_server_set", p)
# print(time.time()-it, "s")
# it = time.time()
# # print(G.get("socket_server_set")[0]['label'])
# print(time.time()-it, "s")
# print(type(True))
# o = ["dd"]
# if type(False) == type(True):
#     print("1")
# # print(p)
# G.set_map("socket_server_set", p)
# print(G.get("socket_server_set"))
# p.append({"lskad":333})
# G.set_map("socket_server_set", p)
# print(G.get("socket_server_set"))

# R.RH.delete("w1")
# print(R.RH.lindex("w1",0))
exit()
# num = R.RH.llen(config.redis_total_console_list)
# print(num)
# time0 = time.time()
# print(time0)
# if num > 0:
#     command_id = R.RH.lindex(config.redis_total_console_list, 0)
#     print(command_id)
#     print(R.RH.get("flag_" + command_id))
#     val = R.RH.hgetall(command_id)
#     if val:
#         print(val)
#         R.del_TotalConsole(command_id)
#     else:
#         print("del:", command_id)
#         R.del_TotalConsole(command_id)
# print(time.time())
# time0 = time.time() - time0
# print(time0)
# R.RH.set("name", "RRRRRR")
# str = "R"
# str = str*3
# ii=0
# ii += 1
# print(ii)
# print(str)
# print(R.RH.getrange("name", 1, 1))#输出:zhan
# R.RH.setrange("name", 1, "E")
# print(R.RH.get("name"))
exit()
# mail_dist = {}
# mail_dist['oo']=1
# def ii():
#     dist = {
#         'ii': 1,
#         'oo': 0
#     }
#     return dist
# mail_ = ii()
# mail_dist.update(mail_)
# print(mail_dist)
# val = "0"
# par = r'^\+?[1-9][0-9]*$'
# if re.match(par, val):
#     print("true")
#     # return True
# else:
#     print("false")
#     # return False
# exit()
# aa = int(float(R.RH.get(config.redis_ua_pid_endtime + str(3961))))
# name = "aa"
# pp = R.RH.hgetall(config.redis_master_uaid_Hash + str(3961))
# dict_a = {"io":1,"oo":"qw"}
# R.RH.hmset(name, dict_a)
# a=R.RH.hgetall(name)
# a ={"pp":1}
# echo_dist = {}
# if echo_dist.get('data') == None:
#     print(echo_dist.get('data'))
# day = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
# month = datetime.date.today().month
# # 获取当前周
# year = datetime.date.today().year
# today = datetime.date.today()
# day = datetime.date(year, month, day=1)
# today = datetime.date.today()
# first = datetime.date(day=1, month=1, year=today.year)
# lastMonth = first - datetime.timedelta(days=1)
# lastMonthday = datetime.date(lastMonth.year, month=1, day=1)
# print(lastMonth)
# print(lastMonthday)
# ii={}
# ii["qw"]=0
# print(len(ii))
# # pp = int(time.mktime((datetime.date(day, day, day=1)).timetuple()))
# pp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
# print(pp)
# if R.RH.exists(name):
#     a = R.RH.llen(name)
#     b = R.RH.lpop(name)
#     c = R.RH.llen(name)
# else:
#     a = None
#     R.RH.rpush(name, 123)

# print(R.RH.lpop(name))
# print(str(time.time())+str(random.randint(10000, 99999)))
exit()
# try:
#     a = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     print(a)
#     print(len(a))
#     b = time.mktime(time.strptime(a, '%Y-%m-%d %H:%M:%S'))
#     print(b)
#     print(b>99999)
# except:
#     a =0

# random.choice(
# a=time.time()
# R.RH.set("aa", a)
# a = R.RH.get("aa")
# # a=1%2
# print(a)
# print(len(a))
# aa = '%.2f' % 3.4200000000000004
# print(time.time())
# print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
# # print(int(time.mktime(date.timetuple())))
# exit()
# print(time.time())
# y1= [{},{},]
# print(y1)
# qq=["aa"]
# print(qq[0])
# from models.user.sendmail_model import SendmailModel
# sendH = SendmailModel()
# sendH.email_send(["99051131@qq.com"], "787787", "主策略账号登陆验证码")
# exit()
# for i in y1:
#     print()
# R = RedisClass()
# msg = b'{"type":"order","ukid":"43b0c96d5fc671f833f45b29f8a82327","f2":"2102249469","f5":"af7d87d75ae3914aef3eef6d40b68b53","f6":"1","orderlist":[{"H0":"GBPUSD","H1":"130183514","H2":"1.26018","H3":"1560530928","H4":"0","H5":"0","H6":"0","H7":"0.20","H8":"0","H9":"0","HA":"0","HB":"0","HC":"-3.27","HD":"0","HE":"-128","HF":"-130.8","HG":"-130.4","HJ":"0"},{"H0":"GBPUSD","H1":"130183516","H2":"1.26016","H3":"1560530949","H4":"0","H5":"0","H6":"0","H7":"0.30","H8":"0","H9":"0","HA":"0","HB":"0","HC":"-4.89","HD":"0","HE":"-191.4","HF":"-195.6","HG":"-195","HJ":"0"},{"H0":"GBPUSD","H1":"130183520","H2":"1.26007","H3":"1560530989","H4":"0","H5":"0","H6":"0","H7":"0.10","H8":"0","H9":"0","HA":"0","HB":"0","HC":"-1.63","HD":"0","HE":"-62.9","HF":"-64.3","HG":"-64.09999999999999","HJ":"0"},{"H0":"GBPUSD","H1":"130183908","H2":"1.25955","H3":"1560532219","H4":"0","H5":"0","H6":"0","H7":"0.10","H8":"0","H9":"0","HA":"0","HB":"0","HC":"-1.63","HD":"0","HE":"-57.7","HF":"-59.1","HG":"-58.9","HJ":"0"},{"H0":"GBPUSD","H1":"130195593","H2":"1.25739","H3":"1560757733","H4":"0","H5":"0","H6":"1","H7":"0.10","H8":"0","H9":"0","HA":"0","HB":"0","HC":"0.18","HD":"0","HE":"34.5","HF":"33.2","HG":"34.5","HJ":"0"},{"H0":"EURUSD","H1":"129975225","H2":"1.13208","H3":"1559915301","H4":"1.12096","H5":"1560530900","H6":"1","H7":"0.05","H8":"0","H9":"0","HA":"0","HB":"0","HC":"1.27","HD":"0","HE":"0","HF":"0","HG":"55.6","HJ":"0"}]}\n'
#
# # msg = msg.decode('utf-8')#encode('utf-8')
# msg = msg[:-1]
# print(msg)
# import json
# msg1 = json.loads(msg)
# # msg1 = eval(msg)
# print("h1:%a"% msg1)
# print(msg1['orderlist'])
import datetime
# endtime = int(float(R.RH.get(config.redis_ua_pid_endtime + "3670")))
# print(endtime)
# print(endtime - int(float(time.time())))
# mail_key = R.RH.get("userid")
# R.RH.hset("dic_name","a1","aa")
# R.RH.hset("dic_name","a2","aa")
# S = MySocketModel()
# hh = S.insertMaterAuthorizeSocketQueue("3670")
# R.RH.sadd(config.redis_socket_queue, "123")
# R.RH.sadd(config.redis_socket_queue, "321")
# print(R.RH.sismember(config.redis_socket_queue, "13"))
# hh = R.RH.keys(pattern=config.redis_master_uaid_Hash+'*')
# print(hh)
# yy = R.RH.hgetall("Hash_master_copy_uaid_3670")
# # for i in range(R.RH.llen(config.redis_socket_queue)):
# #     print(S.getSocketQueue())
# #
# # print(R.RH.exists("ppp"))
# print(R.RH.smembers(config.redis_socket_queue))
# from models.user.order_model import OrderModel
# O = OrderModel()
# h1 = O.get_PositionOrder(3670)
# print(h1)
# print(R.chick_MaterAuthorize(3670, 3731))
# print(R.get_orders_redis(3670))
# # M = MasterModel()
# # M.getMaterFollow(uaid)
# # M.getVcmial(umail, uaid)
# yy = R.RH.hgetall(config.redis_master_uaid_Hash + "3670")
# yy = R.get_orders_redis(3670)
# yy = "{u=1}"
# for y in yy:
#     print(y)
# yy="9,9,9,"
# print(yy[0:-1])
# exit()
import re
# par = "[0-9].+"
par = "[a-zA-Z\d]+$"
str1 ="17bce201dac6db8e0681ec7f9e156c89"
# arr1 = re.compile(par).findall(str1)
print(len(str1))
# a = None
# print(int(a))
# print(str1.isdigit())
# print(str1.encode(encoding='UTF-8').isalnum())
# print(arr1[0])
# exit()
# sockets = tornado.netutil.bind_sockets(9204)
# task_id = tornado.process.fork_processes(2)
# print(task_id)

# umail = "ja.dl.f-879@8kad.cop"
# par = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"
# par2 =r'^[\.a-zA-Z0-9_\-]{1,30}@[a-zA-Z0-9_\-]+\.([a-zA-Z0-9_\-]{1,5})$'
if re.match(par, str1):
    print("y")
else:
    print("N")

exit()
# def getProduct():
#     mysql = mysql_open()
#     cursor = mysql.conn.cursor(cursor=pymysql.cursors.DictCursor)
#     sql = "SELECT pid,qq,version FROM product"
#     cursor.execute(sql)
#     datas = cursor.fetchall()
#     cursor.close()
#     return datas
#
# def setRedisProduct(datas):
#     R = RedisClass()
#     print(datas)
#     for Pdata in datas:
#         print(Pdata)
#         R.RH.set(redis_qq_pid + str(Pdata['pid']), Pdata['qq'])
#         R.RH.set(redis_version_pid + str(Pdata['pid']), Pdata['version'])

# ioloop = IOLoop.instance()
# setRedisProduct(ioloop.run_sync(getProduct))
# datas = getProduct()
# setRedisProduct(datas)
# time_md5 = time.mktime(time.strptime('2019-03-14 22:46:25', "%Y-%m-%d %H:%M:%S"))
# print(time_md5)
from tornado import gen
r = RedisClass()
# r.RH.delete("*")
# print(r.RH.keys(pattern='*'))
# r.RH.set(config.redis_version_pid + "47","1.1")
# exit()
from models.user.order_model import OrderModel
# O= OrderModel()
# O.UpdataOrderToRedis(r, 3670)
# r.RH.hdel(config.redis_master_uaid_dic, "3a07184bd4b83aec9f27428c1e4d9fd5")
# print(r.RH.hget(config.redis_master_uaid_dic, "3a07184bd4b83aec9f27428c1e4d9fd5"))
# print(r.RH.hget(config.redis_master_uaid_Hash + str(3670), str(3671)))
# print(r.RH.smembers(config.redis_order_set + str(3670)))
# print(r.RH.hgetall(config.redis_order_dic + str(468504)))
# M = MasterModel()
# pp = M.getMaterUaid("990ad1b91acb61c7278b18eed7ad2406")

# print(pp)
# exit()
# print(r.RH.hget("acount_","3dd022f45a3185e77eaac914c714f002"))
# print(r.RH.keys("*"))
aou = "63"
# oid = "10"
str_y = "a_" + aou
# # # start_for = time.time()
r.RH.sadd(str_y, 8,9,10,0)
# # r.RH.delete(str_y)
# r.RH.srem(str_y,"0")
# y1 = "1,2,3,4"
# r.RH.sadd("yy", 8)
# print(r.RH.smembers("yy"))
# print(r.RH.sismember("yy",8))
# print(r.RH.sdiff(str_y, "yy"))
# end_for = time.time()
# print('Running time: %s Seconds' % (end_for - start_for))
lll = r.RH.smembers(str_y)
# for item in lll:
#     print(item)
print(lll)
# str_o = "o" + oid
# y = {'iih':98765, 'ajjkhk':'jkkk'}
# y2 = {'iih':1234, 'ajjkhk':'iiiii'}
# #
# # # start_for = time.time()
# r.RH.hset("dic_name",123,"aa")
# r.RH.hdel("dic_name",123)
# # print(r.RH.hexists("dic_name","a1"))
# # r.RH.set("session1", "jdjdj", ex=30)
# print(r.RH.hget("dic_name", "123"))
exit()
# # end_for = time.time()
# # print('Running time: %s Seconds' % (end_for - start_for))
#
# start_for = time.time()
# p1 = r.RH.hgetall("o10")
# p2 = r.RH.hgetall("o11")
# p=[]
# p.append(p1)
# p.append(p2)
# end_for = time.time()
# print('Running time: %s Seconds' % (end_for - start_for))
# print(r.RH.hgetall("o10"))
# print(r.RH.hgetall("o9"))
# print(p)
# print(r.RH.get("user"))
# r.RH.hdel(str_o, "ajjkhk")
# # print(r.RH.hgetall(str_o))
# r.RH.sadd("acount_" + "c9c17f2708f726efd5fa64c15596fefe", 98)
# r.RH.sadd("m_key", 98)
# print(r.RH.sismember(str_y,1))
# print(r.RH.hget(redis_acount_md5_dic,"97faa1f4fc945b34ada90ebbf638db79"))
# print(r.RH.hgetall(redis_acount_md5_dic))
# print(r.RH.hvals(redis_acount_md5_dic))
print(r.RH.exists("yy"))
yy = {"11":0,"12":9}
lpush
for i in r.RH.smembers("yy"):
    r.RH.srem("yy", i)
if r.RH.exists("yy")==0:
    print("kkkk")
    # r.RH.delete(i)
# print(r.RH.get("uaid_endtime_3626"))
# print(r.RH.keys("qq*"))
# r.RH.srem("m_key",98)
# print(r.RH.smembers("m_key"))
# print(r.RH.keys(pattern='o*'))
# # r.RH.delete('o9')
# import hashlib
# uu = str(time.time()*100000)
# print(hashlib.md5(uu.encode(encoding='UTF-8')).hexdigest())
# print(time.time()*100000)
# import os
# print(os.path.join(os.path.abspath('.'), "templates"))
# print(time.time())
# sql = "SELECT * FROM usercode WHERE ptname='%s' AND account=%s AND accountserver='%s' AND vipid=1" % ('kudka', 987987, 'accountserver')
# print(sql)
