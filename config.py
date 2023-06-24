# coding=utf-8

WEBSITE_NAME = "外汇跟单系统管理区-浩外大叔官网"
settings = dict(
    debug=False,  # 设置debug启动方式
    template_path="templates",  # 设置模板路径os.path.join(os.path.abspath('.'),
    static_path="static",  # 设置静态文件路径
    # ui_methods=uimethod, #配置html文件函数调用模块
    index_url="/",  #重定向到首页面
    # log_function=log_request,#自定义tornado
    # packet的配置
    # pycket ={
    #     "engine": "redis",  # 配置存储类型
    #     "storage": {
    #         "host": "localhost",
    #         "port": 6379,
    #         "db_sessions": 5,
    #         "db_notifications": 11,
    #         "max_connections": 2 ** 31
    #     },
    # },
    cookie_secret="Z]Wuu(F%YYo.2r+8DAI<`|T}}k[TR?U1G_?7KRh8k(:.|k4]7;(Y-hF+jDlXc O!",
    xscf_cookies=True,
    IPV4_ONLY=True
)
#MQSQL数据库参数
MYSQL_INFO = {
    "host": "64.31.63.220",
    "port": 33161,
    # "host": "192.168.68.22",# 深圳
    # "port": 3316,
    "user": "root",
    "password": "nL5vTUcPLZbmuVht",
    "db": "copy6"
}
#redis参数
REDIS_INFO = {
    "host": "64.31.63.220",
    "port": 6379
    # "host": "127.0.0.1",# 内网
    # "port": 6379
    # "host": "103.39.220.138",# 深圳
    # "port": 9389
}
# 返回给EA的IP访问地址
Server_IP = "64.31.63.252:9008"
# 时间加密因子
TineMd5Info = 1561697191
# 时间加密因子
ServerMd5Info = "WZ12KfOkMIbwXiRm84gGIUHGEPie4klyX"
# 产品ID
PID = 51
# 返点基数
PROXY_PRICE = 10
IMGURL = "/static/faceimg"
# 错误间隔时间
ERROR_TIME = 21
SOCKET_PORT = 9000
# 发送字符串结束
StringEnd = "....."
# socket发送队列,
# 用rpush(name,values)插入uaid的名称，
# 用llen(name)返回列表个数，
# 用lpop(name)返回uaid的名称。
redis_socket_queue = "redis_socket_queue"
# 账户MD5对应的uaid集合
redis_acount_md5_dic = "acount_"
# 账户uaid的set集合
redis_uaid_set = "set_uaid_"
# 策略账户的登陆验证码set
redis_session_uaid_set = "session_uaid"
# 策略账户key_ma与uaid的集合
redis_master_uaid_dic = "master_uaid"
# 策略账户uaid的set
redis_master_uaid_set = "set_master_uaid"
# 策略账户 可授权的uaid与状态的集合   #Hash 跟单账户所有
redis_master_uaid_Hash = "Hash_master_copy_uaid_"
# 账户uaid对应socket的end_loging_time
redis_ua_socket_end_login_time = "uaid_socket_e_l_time_"
# 账户uaid对应endtime
redis_ua_pid_endtime = "uaid_endtime_"
# order_ID的set集合
redis_order_set = "set_order_"# +str(uaid)
# order的set集合Cache
redis_order_Cache_set = "set_order_cache_"
# 单条order的dic集合
redis_order_dic = "dic_order_" #str(orderid)
# 产品对应QQ
redis_qq_pid = "qq_"
# 产品对应版本
redis_version_pid = "version_"
# 总控制客户端的动作列表,rpush(name,values),lpop(name),llen(name)
redis_total_console_list = "total_console_list"

#sessions时间S
SessionsOutTime = 3600


# 服务器列表
# socket_server_set
socket_server_dist = "socket_server_dist"
server_list = [
    {
    'id': 0,
    'url': '64.31.63.6',#localhost
    'port': 9000
},
    {
    'id': 1,
    'url': '137.74.87.229',
    'port': 9000
},
#     {
#     'id': 2,
#     'url': '127.0.0.1',
#     'port': 9000
# },
#     {
#     'id': 3,
#     'url': '127.0.0.1',
#     'port': 9001
# },
#     {
#     'id': 4,
#     'url': '127.0.0.1',
#     'port': 9002
# }
]
# tornado系统日志格式
# import os
# import tornado
# tornado.options.options.logging = "debug"  # 日志等级 "debug|info|warning|error|none"
# tornado.options.options.log_rotate_mode = "time"
# tornado.options.options.log_rotate_when = "D"  # 时间单位 "other options:('S', 'M', 'H', 'D', 'W0'-'W6')"
# tornado.options.options.log_rotate_interval = 5  # 间隔
# # tornado.options.options.log_file_prefix = "%s/log/" % os.path.dirname(os.path.abspath(__file__))  # 文件名
# tornado.options.options.log_file_num_backups = 10  # 间隔
# tornado.options.options.log_to_stderr = False  # 输出到屏幕  持仓对像转存历史对象128878138
