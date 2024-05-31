# coding = utf-8
import re
import time
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import LoginForm
from models.admin.admin_model import ManagerModel
import json
import logging


logger = logging.getLogger('Main')
class AdminHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        # print(self.request.host)
        # tornado.locale.set_default_locale("en_US")

        User_Agent = self.request.headers.get('User-Agent')
        # self.write(User_Agent)
        # self.finish()
        # if (re.findall("10_15_7", User_Agent) == [] or re.findall("Mozilla/5.0", User_Agent) == []) and (re.findall("15_7", User_Agent) == [] or re.findall("Mac", User_Agent) == []):
        #     # print("非法入侵，将追究法律责任！")
        #     self.redirect("/index")
        #     return
        page_main = {}
        page_main['title_website'] = config.WEBSITE_NAME + "管理区"
        # page_main['User_Agent'] = User_Agent
        if self.session['ManagerUid'] == None:
            yield self.render("admin/login.html", page_main=page_main)
            self.session['_xsrf'] = self.xsrf_token
            return
        else:
            # cookie_dist = self.getCookie()
            # page_main.update(cookie_dist)
            # print("index:%s" % page_main)
            yield self.render('admin/index.html', page_main=page_main, session=self.session)
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
            echo_dist['echo'] = "退出成功"

        else:
            #登陆
            User_Agent = self.request.headers.get('User-Agent')
            # if (re.findall("10_15_7", User_Agent) == [] or re.findall("Mozilla/5.0", User_Agent) == []) and (
            #         re.findall("14_7", User_Agent) == [] or re.findall("Mozilla/5.0", User_Agent) == []):
            #     # print("非法入侵，将追究法律责任！")
            #     return
            #     self.finish()
            F = LoginForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                if tornado.escape.to_unicode(self.request.arguments['_xsrf'][0]) != self.session['_xsrf']:
                    echo_dist['echo'] = "验证失败"
                    echo_dist['reponse_status'] = 1
                else:
                    M = ManagerModel()

                    ManagerArr = yield M.chickLoginPass(F.umail.data, F.password.data)
                    # 验证码检查
                    logger.debug("ManagerArr:%s" % ManagerArr)
                    if ManagerArr:
                        self.session['ManagerUid'] = ManagerArr['uid']
                        self.session['ManagerAid'] = ManagerArr['admin_id']
                        self.session['ManagerFaceurl'] = ManagerArr['faceurl']
                        self.session['ManagerUname'] = ManagerArr['uname']
                        from models.public.headers_model import LogsModel
                        LogsModel.addMysqlLog("Managerlogin", "loging", str(ManagerArr['uid']), self.get_user_ip())
                        echo_dist['echo'] = "登陆成功"
                        echo_dist['reponse_status'] = 5
                    else:
                        echo_dist['echo'] = "登陆失败"
                        echo_dist['reponse_status'] = 1
                self.session['_xsrf'] = ""
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1

        self.write(json.dumps(echo_dist))
        self.finish()