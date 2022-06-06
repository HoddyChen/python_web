#coding=utf-8
import redis
import config
import hashlib
from tornado import gen
# import datetime
import time

class RedisClass:
    # redis 包
    RedisPool = None
    def __init__(self):
        # self.RH = redis.StrictRedis(host='localhost', port=6379)127.0.0.1:6379
        #localhost笔记本
        #127.0.0.1本机
        #192.168.68.46内网
        try:
            RedisPool = redis.ConnectionPool(host=config.REDIS_INFO["host"], port=config.REDIS_INFO["port"], decode_responses=True)
            self.RH = redis.StrictRedis(connection_pool=RedisPool)
            # print("RedisClass__init__")
        except Exception as err:
            pass
        # print(RH.client_list())  # 可以看出两个连接的id是一致的，说明是一个客户端连接

    def __del__(self):
        try:
            self.RH.connection_pool.disconnect()
            # print("RedisClass__del__")
        except Exception as err:
            # print("RedisClass__del__:err:%s" % err)
            pass

    @gen.coroutine
    def insert_master_uaid(self, key_ma, uaid):
        # print(str(uaid))
        self.RH.sadd(config.redis_master_uaid_set, str(uaid))
        self.RH.hset(config.redis_master_uaid_dic, key_ma, str(uaid))
        return

    @gen.coroutine
    def insert_master_Comment(self, key_ma, comment):
        # print(str(uaid))
        self.RH.hset(config.redis_master_uaid_dic, "comment_" + key_ma, str(comment))
        return

    @gen.coroutine
    def delete_redis(self, redis_str):
        #删除类似
        for i in self.RH.keys(redis_str + "*"):
            self.RH.delete(i)
        return True

    @gen.coroutine
    def get_orders_redis(self, uaid):
        #获得uaid所有订单ID
        orders_list = []
        if self.RH.sismember(config.redis_master_uaid_set, uaid):
            for i in self.RH.smembers(config.redis_order_set + str(uaid)):
                orders_list.append(self.RH.hgetall(config.redis_order_dic + str(i)))
        return orders_list

    @gen.coroutine
    def chick_MD5_uaid(self, AccountNumber, md5_from, ukid):
        # 验证
        md5_str = AccountNumber + str(config.TineMd5Info)
        str_md5 = hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()
        # print(md5_from,str_md5)
        if md5_from == str_md5:
            if self.RH.hexists(config.redis_acount_md5_dic, ukid):
                uaid = self.RH.hget(config.redis_acount_md5_dic, ukid)
                # print("uaid:",uaid)
                if uaid:
                    uaid = int(uaid)
                    try:
                        if uaid > 0:
                            # 更新在线时间
                            self.set_redis_ua_OnlineTime(uaid)
                            return uaid
                        else:
                            return -5
                    except Exception as e:
                        return -4
                else:
                    return -3
            else:
                return -2
        else:
            return -1

    @gen.coroutine
    def set_MaterFollow(self, followid, uaid, handle_type):
        # followid是策略iD，
        if handle_type == -1:
            self.RH.hdel(config.redis_master_uaid_Hash + str(followid), str(uaid))
        else:
            self.RH.hset(config.redis_master_uaid_Hash + str(followid), uaid, str(handle_type))
        return

    # 设置最新在线时间
    @gen.coroutine
    def set_redis_ua_OnlineTime(self, uaid):
        # self.RH.set(config.redis_ua_socket_end_login_time + str(uaid),
        #             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.RH.set(config.redis_ua_socket_end_login_time + str(uaid), int(time.time()))
        return

    #得到uaid
    @gen.coroutine
    def get_Mater_uaid(self, key_ma):
        uaid = self.RH.hget(config.redis_master_uaid_dic, key_ma)
        if uaid == None:
            from models.my_socket.my_socket_model import MySocketModel
            M = MySocketModel()
            uaid, comment = yield M.getMaterUaid(key_ma)
            if uaid == None:
                return None
            else:
                self.insert_master_uaid(key_ma, uaid)
                self.insert_master_Comment(key_ma, comment)
        return uaid

    #得到用户自定义备注
    @gen.coroutine
    def get_Mater_Comment(self, key_ma):
        comment = self.RH.hget(config.redis_master_uaid_dic, "comment_" + key_ma)
        return comment

    @gen.coroutine
    def chick_MaterAuthorize(self, mater_id, uaid):
        #检查策略账户的授权
        flag = self.RH.hget(config.redis_master_uaid_Hash + str(mater_id), str(uaid))
        if flag == 1 or flag == "1":
            return True
        else:
            return False

    @gen.coroutine
    def get_MaterAuthorize(self, uaid):
        #返回策略账户的授权状态（所有）
        return self.RH.hgetall(config.redis_master_uaid_Hash + str(uaid))


    @gen.coroutine
    def set_Master_order(self, uaid, datas):
        # print(datas)
        if datas != None:
            for datas_dic in datas:
                # 订单ID集合
                # print(datas_dic)
                self.RH.sadd(config.redis_order_Cache_set + str(datas_dic['uaid']), datas_dic['tid'])
                self.RH.sadd(config.redis_order_set + str(datas_dic['uaid']), datas_dic['tid'])
                # 订单详情
                self.RH.hmset(config.redis_order_dic + str(datas_dic['tid']), datas_dic)
            # 删除订单中已经平仓的单子
            for del_datas in self.RH.sdiff(config.redis_order_set + str(uaid), config.redis_order_Cache_set + str(uaid)):
                # print("del_datas:%s" % del_datas)
                self.RH.srem(config.redis_order_set + str(uaid), del_datas)
                self.RH.delete(config.redis_order_dic + del_datas)
            self.RH.delete(config.redis_order_Cache_set + str(uaid))
            # print(self.RH.smembers(config.redis_order_set + str(datas_dic['uaid'])))
            return True
        else:
            return None

    #写入Redis，策略账号的所有可用跟单账户
    @gen.coroutine
    def getRedisMaterFollow(self, datas):
        # R = RedisClass()
        # # 清除redis_master_AuthorizeUaid_set旧的数据
        # if R.RH.exists(config.redis_master_AuthorizeUaid_set + str(datas[0]['followid'])):
        #     R.RH.delete(config.redis_master_AuthorizeUaid_set + str(datas[0]['followid']))
        echotext = ""
        for data in datas:
            # 写入redis_master_AuthorizeUaid_set新数据
            if data['f_flag'] == 1:
                if data['follow_flag'] == 1:
                    yield self.set_MaterFollow(data['followid'], data['uaid'], 1)
                else:
                    yield self.set_MaterFollow(data['followid'], data['uaid'], 0)
                echotext = echotext + str(data['account']) + "," + str(data['uaid']) + "," + str(data['follow_flag']) + ","
            else:
                yield self.set_MaterFollow(data['followid'], data['uaid'], -1)
            self.RH.sadd(config.redis_master_uaid_set, data['uaid'])
        return echotext


    @gen.coroutine
    def insertMaterAuthorizeSocketQueue(self, master_id):
        # 添加 策略的跟单账户状态为1进入队列
        uaid_arr = yield self.get_MaterAuthorize(master_id)
        # print(uaid_arr)
        for uaid in uaid_arr:
            # print(":", uaid)
            # print("uaid_arr[uaid]", uaid_arr[uaid])
            if uaid_arr[uaid] == "1" or uaid_arr[uaid] == 1:
                # print(uaid)
                self.RH.sadd(config.redis_socket_queue, str(uaid))
        # print(self.RH.smembers(config.redis_socket_queue))
        return True

    # @gen.coroutine
    # def getMaterParameter(self, master_id, pid):
    #     # 获得策略参数
    #     from models.user.master_model import MasterModel
    #     M = MasterModel()
    #     data = yield M.getMaterCopyInfo(master_id, pid)
    #     if data != None:
    #         return data
    #     else:
    #         return None

    # 添加总服务器命令
    @gen.coroutine
    def add_TotalConsole(self, total_dist):
        if total_dist:
            command_id = yield self.add_TotalConsole_list()
            # print(total_dist)
            # print(command_id)
            self.RH.hmset(command_id, total_dist)
            flag_str = "R" * len(config.server_list)
            self.RH.set("flag_" + command_id, flag_str)
            return True
        else:
            return False

    # 重置总服务器命令的状态
    # @gen.coroutine
    def ResetTotalConsole(self):
        command_id = self.RH.lindex(config.redis_total_console_list, 0)
        if command_id:
            flag_str = "R" * len(config.server_list)
            self.RH.set("flag_" + command_id, flag_str)
        return

    # 返回一条总服务器命令
    # @gen.coroutine
    def pop_TotalConsole(self, client_id):
        # while True:
        command_id = self.RH.lindex(config.redis_total_console_list, 0)
        # command_id = self.pop_TotalConsole_list()
        # print(command_id)
        if command_id:
            # print(self.RH.get("flag_" + command_id))
            # print("E" * len(config.server_list))
            if self.RH.get("flag_" + command_id) == "E" * len(config.server_list):
                self.del_TotalConsole(command_id)
            else:
                if self.RH.getrange("flag_" + command_id, client_id, client_id) == "R":
                    self.RH.setrange("flag_" + command_id, client_id, "P")
                    return self.RH.hgetall(command_id)
            return None
        else:
            return None

    # 最后，总服务器命令后的处理
    @gen.coroutine
    def set_EndTotalConsole(self, client_id):
        command_id = self.RH.lindex(config.redis_total_console_list, 0)
        if self.RH.exists("flag_" + command_id):
            # print("=1=")
            self.RH.setrange("flag_" + command_id, client_id, "E")
            # print("=2=")
            if self.RH.get("flag_" + command_id) == "E"*len(config.server_list):
                yield self.del_TotalConsole(command_id)
                # self.pop_TotalConsole_list()
        return


    # 出错时完
    @gen.coroutine
    def set_ErrTotalConsole(self, client_id):
        command_id = self.RH.lindex(config.redis_total_console_list, 0)
        if self.RH.exists("flag_" + command_id):
            self.RH.setrange("flag_" + command_id, client_id, "R")
        return

    @gen.coroutine
    def add_TotalConsole_list(self):
        import random
        command_id = "comm_id" + str(time.time()) + str(random.randint(10000, 99999))
        self.RH.rpush(config.redis_total_console_list, command_id)
        return command_id

    @gen.coroutine
    def pop_TotalConsole_list(self):
        return self.RH.lpop(config.redis_total_console_list)

    #添加命令队列
    @gen.coroutine
    def add_Console_list(self, total_dist):
        if total_dist:
            import random
            for server_arr in config.server_list:
                # print(str(server_arr['id']))
                command_id = "con_id" + str(time.time()) + str(random.randint(10000, 99999))
                self.RH.hmset(command_id, total_dist)
                self.RH.rpush("Console_list" + str(server_arr['id']), command_id)
            return True
        else:
            return False

    # 弹出最左边的命令
    # @gen.coroutine
    def pop_Console_list(self, id):
        con_id = self.RH.lpop("Console_list"+str(id))
        # print("con_id:%s" % con_id)
        if con_id:
            con_dist = self.RH.hgetall(con_id)
            self.RH.delete(con_id)
            return con_dist
        else:
            return {}

    @gen.coroutine
    def del_TotalConsole(self, command_id):
        try:
            if self.RH.exists(command_id):
                self.RH.delete(command_id)
            if self.RH.exists("flag_" + command_id):
                self.RH.delete("flag_" + command_id)
            self.RH.lrem(config.redis_total_console_list, 0, command_id)
            # print("del_TotalConsole")
            return True
        except Exception as err:
            # print(err)
            return False

    @gen.coroutine
    def register_socketIP(self, socketIP, socketPost, label):
        # 注册socket服务器IP
        try:
            # 删除相同标志的IP
            for socket_server in self.RH.smembers("socket_server_set"):
                socket_dist = self.RH.hgetall(socket_server)
                if socket_dist != {} and socket_dist.get('label') == label:
                    self.RH.delete(socket_server)
                    self.RH.srem("socket_server_set", socket_server)
                if socket_dist == {}:
                    self.RH.srem("socket_server_set", socket_server)
            # 注册新IP
            ip_str = "sss" + socketIP + str(socketPost)
            ip_str = ip_str.replace(".", "")
            if not self.RH.sismember("socket_server_set", ip_str):
                self.RH.sadd("socket_server_set", ip_str)
            self.RH.hset(ip_str, "host", socketIP)
            self.RH.hset(ip_str, "port", socketPost)
            self.RH.hset(ip_str, "label", label)
            from models.public.headers_model import global_Models
            G = global_Models()
            G.set_map("label", label)
            return True
        except Exception as err:
            # print(err)
            return False

    # @gen.coroutine
    def get_socket_sercerIP(self):
        # 获得socket服务器IP
        sss_list = []
        for sss_name in self.RH.smembers("socket_server_set"):
            sss = self.RH.hgetall(sss_name)
            sss_list.append(sss)
        return sss_list

    @gen.coroutine
    def Logout_socketIP(self, socketIP, socketPost):
        # 注销socket服务器IP
        for socket_server in self.RH.smembers("socket_server_set"):
            socket_dist = self.RH.hgetall(socket_server)
            if socket_dist != {} and socket_dist.get('host') == socketIP and socket_dist.get('port') == socketPost:
                self.RH.delete(socket_server)
                self.RH.srem("socket_server_set", socket_server)
            if socket_dist == {}:
                self.RH.srem("socket_server_set", socket_server)
        pass