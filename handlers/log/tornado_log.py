import logging
import tornado
# 日志格式
# logging.getLogger().setLevel(logging.INFO)
# formatter = logging.Formatter(fmt="%(levelname).4s %(asctime)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
# handler = logging.StreamHandler()
# handler.setFormatter(formatter)
# logging.getLogger().addHandler(handler)

# 日志消息格式
def log_request(handler):
    if handler.get_status() < 400:
        log_method = logging.info
    elif handler.get_status() < 500:
        log_method = logging.warning
    else:
        log_method = logging.error
    request_time = 1000.0 * handler.request.request_time()
    log_method("%d %s %s (%s) %s %.2fms",
               handler.get_status(), handler.request.method,
               handler.request.uri, handler.request.remote_ip,
               # handler.request.headers["User-Agent"],
               handler.request.arguments,
               request_time)


def init_logging(log_file):
    # 使用TimedRotatingFileHandler处理器
    from logging.handlers import TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(log_file, when="d", interval=1, backupCount=30)
    # 输出格式
    file_handler.suffix = "%Y%m%d_%H.log"
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(lineno)d]  %(message)s"
    )
    file_handler.setFormatter(log_formatter)
    # 将处理器附加到根logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.ERROR)
