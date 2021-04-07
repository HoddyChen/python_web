#coding=utf-8
import tornado.escape
import tornado.websocket
import tornado.web
# from pycket.session import SessionMixin
import traceback
from config import settings
import re

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get_lang(self):
        lang_str = self.get_secure_cookie("lang_str")
        # print(lang_str)
        if lang_str:
            return str(lang_str, encoding="utf-8")
        else:
            lang = self.request.headers.get('Accept-Language')
            par = '[a-zA-Z]+'
            if type(lang) == type("str"):
                # print(type(lang))
                lang_arr = re.compile(par).findall(lang)
            # print(lang_arr[0])
                if lang_arr[0].find("zh") >= 0 or lang_arr[0].find("cn") >= 0 or lang_arr[0].find("ZH") >= 0 or lang_arr[0].find("CN") >= 0:
                    lang_str = "cn"
                else:
                    lang_str = "en"
            else:
                # print("0")
                lang_str = "cn"
            self.set_secure_cookie("lang_str", lang_str, expires_days=99999)
            return lang_str


    def get_current_user(self):
        if self.session["web_uid"]:
            # print(self.session["uname"])
            return self.session["web_uid"]
        else:
            yield self.redirect('user/login.html', permanent=False)

    # def on_finish(self):
    #     self.db.close()

    def get_user_locale(self):
        # _ = self.locale.translate
        # user_locale = self.get_argument('lang', "")
        # self.get_lang()
        if self.get_lang() == 'en':
            lang_type = "en_US"
        else:
            lang_type = "zh_CN"
        # tornado.locale.set_default_locale(lang_type)
        # tornado.locale.get('en_US')
        return tornado.locale.get(lang_type)

    def get_user_ip(self):
        ip = self.request.headers.get("X-Real-IP") or \
             self.request.headers.get("X-Forwarded-For") or \
             self.request.remote_ip
        return ip
        #  ip3 = self.request.headers.get("X-Forwarded-For", "")
        # ip = self.request.headers.get("X-Real-Ip", "")
        # if ip == "":
        #     return self.request.remote_ip
        # else:
        #     return ip

    def write_error(self, status_code, **kwargs):
        error_trace_list = traceback.format_exception(*kwargs.get("exc_info"))

        if settings['debug']:
            # from web.py
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in error_trace_list:
                self.write(line)
            self.finish()
        else:
            # self.exception_nofity(status_code, error_trace_list)
            # by status_code
            if status_code == 500:
                self.render('user/error.html')
                return

            if status_code == 403:
                self.write('sorry, request forbidden!')
                return

            self.render('user/error.html')

        return

    def getCookie(self, flag=0):
        cookie_dist = {}
        cookie_dist['current_strategy'] = None if self.get_secure_cookie('current_strategy' + str(self.session['web_uid'])) == None else str(self.get_secure_cookie("current_strategy" + str(self.session['web_uid'])), encoding="utf-8")
        cookie_dist['current_ma_name'] = None if self.get_secure_cookie('current_ma_name' + str(self.session['web_uid'])) == None else str(self.get_secure_cookie('current_ma_name' + str(self.session['web_uid'])), encoding="utf-8")
        cookie_dist['current_account'] = None if self.get_secure_cookie('current_account' + str(self.session['web_uid'])) == None else str(self.get_secure_cookie('current_account' + str(self.session['web_uid'])), encoding="utf-8")
        cookie_dist['current_key_ma'] = None if self.get_secure_cookie('current_key_ma' + str(self.session['web_uid'])) == None else str(self.get_secure_cookie('current_key_ma' + str(self.session['web_uid'])), encoding="utf-8")
        cookie_dist['current_logo_url'] = "" if self.get_secure_cookie('current_logo_url' + str(self.session['web_uid'])) == None else str(self.get_secure_cookie('current_logo_url' + str(self.session['web_uid'])), encoding="utf-8")
        if cookie_dist['current_strategy'] == None and flag == 0:
            self.redirect("/index")
            return None
        return cookie_dist

# class BaseWebSocket(tornado.websocket.WebSocketHandler, SessionMixin):
#     def get_current_user(self):
#         if self.session.get("username"):
#             return user_model.by_name(self.session.get("username"))
#         else:
#             return None