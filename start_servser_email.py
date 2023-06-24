#coding=utf-8
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.escape
from tornado import gen
from tornado.options import define, options
import logging
from handlers.log.mylog import logInit
from handlers.log.tornado_log import log_request
from handlers.log.tornado_log import init_logging
import os
from wtforms_tornado import Form
from wtforms import StringField, validators, PasswordField, IntegerField, BooleanField, FloatField

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr



class SendEmailForm(Form):
    # 管理员登陆
    umail = StringField('umail', [
        validators.InputRequired(message=(u'邮箱输入不正确，请重新输入')),
        validators.Length(min=5, max=32, message=(u'邮箱字符应为5-32个字符，请重新输入')),
        validators.Email(message=(u'邮箱格式不正确，请重新输入')),
        # validators.Regexp('^((?!\.de).)*$', message=(u'非法数据')),
        validators.Regexp('.*\.(com|cn|net|org|gov|edu|top)$', message=(u'非法数据')),
    ])

class mailHandler(tornado.web.RequestHandler):
    from_mail = "cs@fxcns.com"  # 'cs@fxcns.com'
    from_title = "跟单交易多账户管理系统邮件"
    mail_password = 'o~yA@C@fi&JiUt&jZHVfMOQT2IHyJtuvvjnljOVK~$Zjha6z~lWwS~9g70bqVcgGFUk8j~wouSv`4rfXp@IKhdlTkL9kX&rx$za'

    @gen.coroutine
    def post(self):
        data = self.request.arguments
        self.email_err_send()

    def get(self):
        data = self.request.arguments
        print("1")
        self.email_err_send()

    @gen.coroutine
    def email_err_send(self):
        tomail = ['99051131@qq.com']
        echotext = "Fxncs-发生错误停止运行"
        mailtitle = "Fxncs-发生错误停止运行"
        send_flag = yield self.email_send(tomail, echotext, mailtitle)
        logger.info("send_flag: %s" % send_flag)
        if send_flag == True:
            logger.info("%s,邮件发送成功!" % mailtitle)
        return

    @gen.coroutine
    def email_send(self, to_mail, mail_msg, mailtitle):
        #to_mail必须是列表['']
        message = MIMEText(mail_msg, 'html', 'utf-8')
        message['From'] = formataddr([self.from_title, self.from_mail])
        # message['To'] = ';'.join(to_mail)  # formataddr(["亲", ""])
        message['To'] = formataddr(["dear", to_mail[0]])
        message['Subject'] = mailtitle

        try:
            # smtpObj = smtplib.SMTP('smtp.office365.com', 587)
            # 65.49.208.148:587
            smtpObj = smtplib.SMTP('65.49.208.148', 587)
            # smtpObj.connect('smtp.office365.com', 587)  # 25 为 SMTP 端口号
            smtpObj.starttls()
            # smtpObj.set_debuglevel(1)# 调试时开启
            smtpObj.login(self.from_mail, self.mail_password)
            smtpObj.sendmail(self.from_mail, to_mail, message.as_string())
            print("邮件发送成功")

            return True
        except smtplib.SMTPException:
            logger.error("Error: 无法发送邮件")
            return False
        finally:
            smtpObj.quit()

    @gen.coroutine
    def email_send_proxy(self, to_mail, mail_msg, mailtitle, from_title2):
        #to_mail必须是列表['']
        message = MIMEText(mail_msg, 'html', 'utf-8')
        message['From'] = formataddr([from_title2, self.from_mail])
        # message['To'] = ';'.join(to_mail)  # formataddr(["亲", ""])
        message['To'] = formataddr(["dear", to_mail[0]])
        message['Subject'] = mailtitle

        try:
            # smtpObj = smtplib.SMTP('smtp.office365.com', 587)
            smtpObj = smtplib.SMTP('65.49.208.148', 587)
            # smtpObj.connect('smtp.office365.com', 587)  # 25 为 SMTP 端口号
            smtpObj.starttls()
            # smtpObj.set_debuglevel(1)# 调试时开启
            smtpObj.login(self.from_mail, self.mail_password)
            smtpObj.sendmail(self.from_mail, to_mail, message.as_string())
            # print("邮件发送成功")

            return True
        except smtplib.SMTPException:
            logger.error("Error: 无法发送邮件")
            return False
        finally:
            smtpObj.quit()


def logInit(path):
    log_path = os.path.join(path, "mail_log.log")
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


handlers = [
    # (r'/', IndexHandler),
    (r'/', mailHandler),
]
#定义一个默认的端口
define("port", default=8000, help="run port ", type=int)
settings = dict(
    debug=True,  # 设置debug启动方式
    template_path="templates",  # 设置模板路径os.path.join(os.path.abspath('.'),
    static_path="static",  # 设置静态文件路径
    # ui_methods=uimethod, #配置html文件函数调用模块
    index_url="/",  #重定向到首页面
    cookie_secret="Z]Wuu(F%YYo.2r+8DAI<`|T}}k[TR?U1G_?7KRh8k(:.|k4]7;(Y-hF+jDlXc O!",
    xscf_cookies=True,
    IPV4_ONLY=True
)
# define("t",  default=False, help="creat tables", type=bool)
log_path = os.path.dirname(os.path.abspath(__file__))

logger = logInit(log_path)
if __name__ == "__main__":
    # sockets = tornado.netutil.bind_sockets(9204)
    # task_id = tornado.process.fork_processes(2)
    # print(task_id)
    # 启动http服务
    options.parse_command_line()
    app = tornado.web.Application(handlers, **settings)
    app.settings["log_function"] = log_request
    http_server = tornado.httpserver.HTTPServer(app)#http

    #http_server.listen(8037)#options.port
    http_server.listen(options.port)
    # http_server.start(0)  # forks one process per cpu
    print('start mail server...')
    init_logging("%s/log/syslog.log" % (os.path.dirname(os.path.abspath(__file__))))
    tornado.ioloop.IOLoop.instance().start()

    # server = HTTPServer(application)
    # server.bind(8888)
    # server.start(4)  # Forks multiple sub-processes
    # tornado.ioloop.IOLoop.current().start()
