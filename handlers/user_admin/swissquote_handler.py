#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import LoginForm
from handlers.myredis.redis_class import RedisClass
from models.user.swissquote_model import SwissquoteModel
import json
import logging

logger = logging.getLogger('Main')
class SwissquoteHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        # print(self.request.host)
        # tornado.locale.set_default_locale("en_US")
        #ip 检测
        # user_ip = yield self.chink_host()
        # if user_ip:
        #     yield self.render("index.html", ip=user_ip)
        #     return
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = self.locale.translate("返佣管理系统")
        if self.session['swissquote_uid'] == None:
            yield self.render("user/swissquote_login.html", page_main=page_main)
            return
        else:
            page_main['title_type'] = self.locale.translate("瑞讯银行瑞士账户申请")
            yield self.render('user/swissquote_index.html', page_main=page_main, session=self.session)
            return
            # print("get:%s" % self.get_secure_cookie("current_strategy"))


    @gen.coroutine
    def post(self):
        echo_dist = {}
        F = LoginForm(self.request.arguments)
        if F.validate():
            S = SwissquoteModel()
            if F.fx_type.data == "signout":
                # 退出
                self.session.delete()
                # self.session['swissquote_uid'] = None
                echo_dist['reponse_status'] = 5
                echo_dist['echo'] = self.locale.translate("退出成功")

            elif F.fx_type.data == "sendmail":
                from models.user.sendmail_model import SendmailModel
                import random
                sendH = SendmailModel()
                mail_key = "".join(random.sample('123567890', 6))
                mail_text = self.locale.translate("返佣管理系统登陆验证码")
                mail_text = mail_text + """：
    
                                """
                mail_text = mail_text + mail_key
                mail_text = mail_text + """
    
                                """
                mail_text = mail_text + self.locale.translate("请不要将验证码转发或给其他人查看")
                mail_text = mail_text + """！！！！！
    
                                -----"""
                mail_text = mail_text + self.locale.translate("来自[返佣管理系统]")
                tomail = []
                tomail.append(F.umail.data)
                send_flag = yield sendH.email_send(tomail, mail_text, self.locale.translate("返佣管理系统登陆验证码"))
                if send_flag == True:
                    R = RedisClass()
                    R.RH.set(config.redis_session_uaid_set + str(F.umail.data), mail_key, ex=config.SessionsOutTime)
                    echo_dist['reponse_status'] = 5  # 发送成功
                else:
                    echo_dist['reponse_status'] = 2  # 发送失败

            else:
            #登陆
                R = RedisClass()
                mail_key = R.RH.get(config.redis_session_uaid_set + str(F.umail.data))
                R.RH.delete(config.redis_session_uaid_set + str(F.umail.data))
                # 验证码检查
                if mail_key == F.pword.data:
                    m_data = yield S.CheckMailAccount(F.umail.data)
                    # print(m_data)
                    if m_data == None:
                        #策略邮箱未注册
                        uid = yield S.AddMailAccount(F.umail.data)
                        if uid == None:
                            echo_dist['reponse_status'] = 0
                            echo_dist['echo'] = self.locale.translate("邮箱注册失败")
                        else:
                            self.session['swissquote_uid'] = uid
                            echo_dist['reponse_status'] = 5
                            echo_dist['echo'] = self.locale.translate("新注册并登陆成功")
                    else:
                        # 已经有账号
                        self.session['swissquote_uid'] = m_data['uid']
                        echo_dist['echo'] = self.locale.translate("登陆成功")
                        echo_dist['reponse_status'] = 5

                    from models.public.headers_model import LogsModel
                    LogsModel.addMysqlLog("login", "loging", str(m_data['uid']), self.get_user_ip())
                else:
                    echo_dist['reponse_status'] = 0
                    echo_dist['echo'] = self.locale.translate("登录失败")

        else:
            # 表单错误
            from models.public.confrom_model import get_ErrorForm
            echo_dist['echo'] = get_ErrorForm(F)
            echo_dist['reponse_status'] = 1
        self.write(json.dumps(echo_dist))
        self.finish()

    @gen.coroutine
    def chink_host(self):
        host = self.request.host
        # par = r'^\+?[1-9][0-9]*$'
        # print(host.find("103.39.220.138"))
        # ip1 = self.request.remote_ip
        # ip2 = self.request.headers.get("X-Real-Ip", "")
        # ip3 = self.request.headers.get("X-Forwarded-For", "")
        # ip = str(ip1) + "," + str(ip2) + "," + str(ip3)
        if host.find("103.39.220.138") >= 0 or host.find("master.6copy.com") >= 0:
            if host.find("127.0.0.1") >= 0:
                ip = self.get_user_ip()
                if ip == "103.86.46.13":
                    return None
                else:
                    return ip
            # return True
        return None
        # import re
        # if re.match(par, host):
        #     print(host)
        #     ip = self.get_user_ip()
        #     yield self.render("index.html", ip=ip)
        # return