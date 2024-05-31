#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import LoginForm
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel
from models.user.strategy_model import StrategyModel
import json
import logging

logger = logging.getLogger('Main')
class AdminHandler(SessionHandler, BaseHandler):

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
        page_main['title_website'] = config.WEBSITE_NAME
        if self.session['web_uid'] == None:
            yield self.render("user/login.html", page_main=page_main)
            self.session['_xsrf'] = self.xsrf_token
            return
        else:
            from models.public.confrom_model import StrategySelectForm
            F = StrategySelectForm(self.request.arguments)
            if F.validate():
                # 选定策略，并设置cookie
                # print("F")
                if F.fx_type.data == "strategy_select":
                    S = StrategyModel()
                    s_data = yield S.getStrategyInfo(self.session['web_uid'], F.form_uaid.data, None)
                    if s_data != None:
                        logger.debug("set:%s" % F.form_uaid.data)
                        self.set_secure_cookie("current_strategy" + str(self.session['web_uid']), str(F.form_uaid.data))
                        self.set_secure_cookie("current_ma_name" + str(self.session['web_uid']), "null" if s_data['ma_name'] == None else s_data['ma_name'])
                        self.set_secure_cookie("current_account" + str(self.session['web_uid']), "null" if s_data['account'] == None else s_data['account'])
                        self.set_secure_cookie("current_key_ma" + str(self.session['web_uid']), "null" if s_data['key_ma'] == None else s_data['key_ma'])
                        self.set_secure_cookie("current_logo_url" + str(self.session['web_uid']), "null" if s_data['logo_url'] == None else s_data['logo_url'])
                        if len(F.backurl.data) > 0:
                            self.redirect(F.backurl.data)
                        else:
                            self.redirect("/index")
                        return
                    else:
                        yield self.render('user/strategy_select.html', page_main=page_main, session=self.session)
                        return
                elif F.fx_type.data == "login":
                    self.redirect(F.backurl.data)
                    return
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                logger.error(get_ErrorForm(F))
                self.render('user/500.html')
                return
            # print("get:%s" % self.get_secure_cookie("current_strategy"))
            if self.get_secure_cookie("current_strategy" + str(self.session['web_uid'])) == None:
                S = StrategyModel()
                s_data = yield S.getStrategyList(self.session['web_uid'])
                page_main['s_data'] = s_data
                if len(s_data) == 0:
                    self.session.delete()
                    yield self.render("user/login.html", page_main=page_main)
                    self.session['_xsrf'] = self.xsrf_token
                    return
                elif len(s_data) == 1:
                    self.set_secure_cookie("current_strategy" + str(self.session['web_uid']), str(s_data[0]['uaid']))
                    self.set_secure_cookie("current_ma_name" + str(self.session['web_uid']), "null" if s_data[0]['ma_name'] == None else s_data[0]['ma_name'])
                    self.set_secure_cookie("current_account" + str(self.session['web_uid']), "null" if s_data[0]['account'] == None else s_data[0]['account'])
                    self.set_secure_cookie("current_key_ma" + str(self.session['web_uid']), "null" if s_data[0]['key_ma'] == None else s_data[0]['key_ma'])
                    self.set_secure_cookie("current_logo_url" + str(self.session['web_uid']), "null" if s_data[0]['logo_url'] == None else s_data[0]['logo_url'])
                    page_main['current_strategy'] = str(s_data[0]['uaid'])
                    page_main['current_ma_name'] = s_data[0]['ma_name']
                    page_main['current_account'] = s_data[0]['account']
                    page_main['current_key_ma'] = s_data[0]['key_ma']
                    page_main['current_logo_url'] = s_data[0]['logo_url']
                    yield self.render('user/index.html', page_main=page_main, session=self.session)
                    return
                else:
                    # 多个策略，未曾指定，转指定
                    yield self.render('user/strategy_select.html', page_main=page_main, session=self.session)
                    return
            else:
                cookie_dist = self.getCookie()
                page_main.update(cookie_dist)
                # print("index:%s" % page_main)
                yield self.render('user/index.html', page_main=page_main, session=self.session)
                return


    @gen.coroutine
    def post(self):
        type = self.get_argument("type", "")
        echo_dist = {}
        if type == "sign_out":
            # 退出
            self.session.delete()
            # self.session['web_uid'] = None
            # self.session['web_uaid'] = None
            # self.session['web_key_ma'] = None
            # self.session['web_account'] = None
            # self.session['web_email'] = None
            # self.session['web_uname'] = None
            echo_dist['reponse_status'] = 5
            echo_dist['echo'] = self.locale.translate("退出成功")

        else:
            #登陆
            F = LoginForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                if tornado.escape.to_unicode(self.request.arguments['_xsrf'][0]) != self.session['_xsrf']:
                    echo_dist['echo'] = "验证失败"
                    echo_dist['reponse_status'] = 1
                else:
                    R = RedisClass()
                    mail_key = R.RH.get(config.redis_session_uaid_set + str(F.umail.data))
                    R.RH.delete(config.redis_session_uaid_set + str(F.umail.data))
                    # 验证码检查
                    if mail_key == F.pword.data:
                        M = MasterModel()
                        m_data = yield M.checkMaterMail(F.umail.data)
                        # print(m_data)
                        if len(m_data) == 0:
                            echo_dist['reponse_status'] = 0
                            echo_dist['echo'] = self.locale.translate("策略邮箱未注册")
                        else:
                            self.session['web_uid'] = m_data[0]['uid']
                            uaid_list = ""
                            key_ma_list = ""
                            ma_list = ""
                            for data in m_data:
                                uaid_list = uaid_list + str(data['uaid']) + ","
                                key_ma_list = key_ma_list + data['key_ma'] + ","
                                ma_list = ma_list + data['account'] + ","
                            self.session['web_uaid'] = uaid_list
                            # self.session['web_key_ma'] = key_ma_list
                            # self.session['web_account'] = ma_list
                            self.session['web_email'] = F.umail.data
                            self.session['web_uname'] = m_data[0]['uname']
                            from models.public.headers_model import LogsModel
                            LogsModel.addMysqlLog("login", "loging", str(m_data[0]['uid']), self.get_user_ip())
                            echo_dist['echo'] = self.locale.translate("登陆成功")
                            echo_dist['reponse_status'] = 5
                #self.session['_xsrf'] = ""
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