#coding=utf-8
#用户信息解析
import config
from tornado import gen
from handlers.myredis.redis_class import RedisClass
import json
import datetime
from libs.db.dbsession import pool
from tornado import gen

class global_Models():
    # 拼装成字典构造全局变量  借鉴map  包含变量的增删改查
    map = {}

    # @classmethod
    def set_map(self, key, value):
        if (isinstance(value, dict)):
            value = json.dumps(value)
        self.map[key] = value

    def set(self, keys):
        try:
            # print(keys)
            for key_, value_ in keys.items():
                self.map[key_] = value_
                # self.logger.debug(key_ + ":" + str(value_))
        except BaseException as msg:
            # self.logger.error(msg)
            raise msg

    def set_keys(self, key0, items1, keys2):
        try:
            # print(keys)
            # for key_, value_ in keys1.items():
            for i, d in enumerate(self.map[keys2]):
                # print(d)
                for x, y in items1.items():
                    # print(x,y)
                    if x == key0:
                        if (d.get(x)) == y:
                            pass
                        else:
                            break
                    # print(x)
                    for j, p in d.items():
                        if x == j:
                            d[j] = y
            # ValueError: no dict with the key and value combination found
        except BaseException as msg:
            # self.logger.error(msg)
            raise msg

    def del_map(self, key):
        try:
            del self.map[key]
            return self.map
        except KeyError:
            pass
            # self.logger.error("key:'" + str(key) + "'  不存在")

    def get(self, *args):
        try:
            dic = {}
            for key in args:
                if len(args) == 1:
                    dic = self.map[key]
                    # self.logger.debug(key + ":" + str(dic))
                elif len(args) == 1 and args[0] == 'all':
                    dic = self.map
                else:
                    dic[key] = self.map[key]
            return dic
        except KeyError:
            # self.logger.error("key:'" + str(key) + "'  不存在")
            return None

    def get_keys(self, key0, items1, keys2):
        try:
            # print(keys)
            # for key_, value_ in keys1.items():
            for i, d in enumerate(self.map[keys2]):
                # print(d)
                for x, y in items1.items():
                    # print(x,y)
                    if x == key0:
                        if (d.get(x)) == y:
                            return d
                        else:
                            break
            # ValueError: no dict with the key and value combination found
        except BaseException as msg:
            # self.logger.error(msg)
            raise msg

    def getall(self, ):
        try:
            return self.map
        except KeyError:
            # self.logger.error('  不存在')
            return None

class Headers_Models():
    # 识别用户设备是不是手机
    @gen.coroutine
    def chick_Mobile(self, user_request, userid, temp_uid):
        yield self.set_Header(user_request, userid, temp_uid)
        if 'Mobile'in user_request.headers['User-Agent']:
            return True
        else:
            return False

    # 记录用户信息
    @gen.coroutine
    def set_Header(self, user_request, userid, temp_uid):
        R = RedisClass()
        if userid == None:
            R.RH.hset(config.redis_user_headers_dic, temp_uid, user_request.headers['Accept-Language'] + " " + user_request.headers['User-Agent'] + " " + user_request.remote_ip)
        else:
            R.RH.hset(config.redis_user_headers_dic, userid, user_request.headers['Accept-Language'] + " " + user_request.headers['User-Agent'] + " " + user_request.remote_ip)
        return

    @gen.coroutine
    def chickLogin(self, id):
        if id == None:
            self.redirect('/conadmin/login', permanent=False)
            # self.finish()
            return False
        else:
            return True


    @gen.coroutine
    def getMktime(self, type):
        import time
        import datetime
        # 获取当前年份
        year = datetime.date.today().year
        # 获取当前月份
        month = datetime.date.today().month
        # 获取当前周
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        now = datetime.datetime.now()
        if type == "theYear":
            return int(time.mktime((datetime.datetime(year, 1, 1)).timetuple()))
        elif type == "theMonth":
            return int(time.mktime((datetime.date(year, month, day=1)).timetuple()))
        elif type == "theWeek":
            return int(time.mktime((today - datetime.timedelta(days=today.weekday())).timetuple()))
        elif type == "lastWeek":
            return int(time.mktime((today - datetime.timedelta(days=today.weekday() + 7)).timetuple()))
        elif type == "lastWeekOne":
            return int(time.mktime((today - datetime.timedelta(days=today.weekday() - 6)).timetuple()))
        elif type == "theDay":
            return int(time.mktime(datetime.date.today().timetuple()))
        elif type == "lastMonth":
            return int(time.mktime(datetime.date(year, month, day=1).timetuple()))
        elif type == "lastMonthOne":
            lastMonth = (datetime.date(year, month, day=1) - oneday)
            return int(time.mktime(datetime.date(lastMonth.year, lastMonth.month, day=1).timetuple()))
        elif type == "lastYear":
            return int(time.mktime(datetime.date(year, month=1, day=1).timetuple()))
        elif type == "lastYearOne":
            lastYear = (datetime.date(year, month=1, day=1) - oneday)
            return int(time.mktime(datetime.date(lastYear.year, month=1, day=1).timetuple()))


    def getOrderNo(self):
        import time
        return str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + str(time.time()).replace('.', '')[-7:]

# 时间转json的处理
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
            # print(obj)
            # return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

# 日志
class LogsModel():
    @staticmethod
    @gen.coroutine
    def addMysqlLog(log_type, sql_text, uid, ip=""):
        # 新增日志
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "INSERT INTO logs_pre(`log_type`,`sql_text`,`add_date`,`uid`,ip)" \
                          " VALUES(%s, %s, NOW(), %s, %s)"
                    # print(sql)
                    yield cursor.execute(sql, (log_type, sql_text, uid, ip))
                    # row = yield cursor.fetchone()
                    # print("row:%s" % row)
                    yield conn.commit()
                except Exception as err:
                    yield conn.rollback()
                    # logger.error("[EditPass] %s" % err)
                    return False
        return True

class DistMD5():
    @staticmethod
    def chickDist(dist_md5):
        # 验证
        import hashlib
        # str_md5 = ""
        str_md5 = dist_md5['fx_type'] + str(dist_md5['sendid']) + str(dist_md5['followid']) + str(dist_md5['label']) + \
                  dist_md5['key2']
        # for key, value in dist_md5.items():
        #     if key != "key":
        #         str_md5 = str_md5 + str(value)
        # print(str_md5)
        md5_str = str_md5 + str(config.TineMd5Info)
        str_md5 = hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()
        if dist_md5['key'] == str_md5:
            return True
        else:
            return False

    @staticmethod
    def encryptDist(dist_md5):
        # 生成验证
        import hashlib
        # str_md5 = ""
        str_md5 = dist_md5['fx_type'] + str(dist_md5['sendid']) + str(dist_md5['followid']) + str(dist_md5['label']) \
                  + dist_md5['key2']
        # for key, value in dist_md5.items():
        #     if key != "key":
        #         str_md5 = str_md5 + str(value)
        # print(str_md5)
        md5_str = str_md5 + str(config.TineMd5Info)
        return hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()