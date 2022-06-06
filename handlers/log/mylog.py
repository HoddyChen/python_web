import logging
import os

def logInit(path):
    log_path = os.path.join(path, "web_log", "web_log.log")
    # print(log_path)
    # logHandler = logging.handlers.TimedRotatingFileHandler(path + "/web_log.log", when="midnight")
    logHandler = logging.handlers.TimedRotatingFileHandler(log_path, when="midnight")
    logHandler.suffix = "%Y%m%d_%H.log"
    logFormatter = logging.Formatter(
        '%(asctime)s {%(name)s} {%(levelname)s} [%(module)s,%(lineno)d,%(funcName)s]%(message)s ')
    logHandler.setFormatter(logFormatter)
    logger = logging.getLogger('Main')
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG)
    return logger


def logInit_socket(path):
    log_path = os.path.join(path, "socket_log", "socket_log.log")
    logHandler = logging.handlers.TimedRotatingFileHandler(log_path, when="midnight")
    # logHandler = logging.handlers.TimedRotatingFileHandler(path + "/socket_log.log", when="midnight")
    logHandler.suffix = "%Y%m%d_%H.log"
    logFormatter = logging.Formatter(
        '%(asctime)s {%(name)s} {%(levelname)s} [%(module)s,%(lineno)d,%(funcName)s]%(message)s ')
    logHandler.setFormatter(logFormatter)
    logger = logging.getLogger('Socket')
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG)
    return logger

def logInit_socket_client(path):
    log_path = os.path.join(path, "socket_client_log", "socket_client_log.log")
    logHandler = logging.handlers.TimedRotatingFileHandler(log_path, when="midnight")
    logHandler.suffix = "%Y%m%d_%H.log"
    logFormatter = logging.Formatter(
        '%(asctime)s {%(name)s} {%(levelname)s} [%(module)s,%(lineno)d,%(funcName)s]%(message)s ')
    logHandler.setFormatter(logFormatter)
    logger = logging.getLogger('Client')
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG)
    return logger

def logInit_socket_robot_client(path):
    log_path = os.path.join(path, "socket_robot_clinet_log", "socket_robot_clinet_log.log")
    logHandler = logging.handlers.TimedRotatingFileHandler(log_path, when="midnight")
    logHandler.suffix = "%Y%m%d_%H.log"
    logFormatter = logging.Formatter(
        '%(asctime)s {%(name)s} {%(levelname)s} [%(module)s,%(lineno)d,%(funcName)s]%(message)s ')
    logHandler.setFormatter(logFormatter)
    logger = logging.getLogger('robot_clinet')
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG)
    return logger
# # 基于python标准库logging
# access_log = logging.getLogger("tornado.access")
# app_log = logging.getLogger("tornado.application")
# gen_log = logging.getLogger("tornado.general")
#
# # 日志输出形式
# DEFAULT_FORMAT = \
#     '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
# DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'
# # 控制台各等级日志颜色
# DEFAULT_COLORS = {
#     logging.DEBUG: 4,  # Blue
#     logging.INFO: 2,  # Green
#     logging.WARNING: 3,  # Yellow
#     logging.ERROR: 1,  # Red
# }