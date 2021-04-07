#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import ProposalForm
from models.public.headers_model import Headers_Models
from models.user.proxy_order_model import ProxyOrderModel
import json
import logging

logger = logging.getLogger('Main')
class ProxyAccountVerifyHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME
        page_main['title_type'] = "账户批量激活"
        if self.session['ManagerUid'] == None:
            # 退出
            # yield self.render("user/login.html", page_main=page_main)
            yield self.render("admin/login.html", page_main=page_main)
            return
        else:
            fx_type = self.get_argument("fx_type", None)
            P = ProxyOrderModel()
            if fx_type:
                # cookie_dist = self.getCookie()
                # page_main.update(cookie_dist)
                page_main['text'] = "账户自动激活程序,非法......"
            else:
                # 第一次
                page_main['one_num'] = yield P.editPAVerify3()
                page_main['text'] = "账户自动激活程序,开始......"
            yield self.render('admin/index_proxy_account_verify.html', page_main=page_main, session=self.session)
            return
        self.finish()

    @gen.coroutine
    def post(self):
        echo_dist = {}
        if self.session['ManagerUid'] == None:
            # 退出
            echo_dist['reponse_status'] = -1
        else:
            # print("SS:", self.request.arguments)
            fx_type = self.get_argument("fx_type", None)
            if fx_type == "edit_verify":
                P = ProxyOrderModel()
                a_data = yield P.getProxyAccount(0)
                if len(a_data) > 0:
                    for a_data_v in a_data:
                        a_flag = yield P.editPAVerify2(a_data_v['account'])
                        if a_flag == 5:
                            echo_dist['echo'] = str(a_data_v['account']) + "激活成功<BR>"
                            echo_dist['reponse_status'] = 5
                        else:
                            echo_dist['echo'] = str(a_data_v['account']) + "激活失败<BR>"
                            echo_dist['reponse_status'] = 5
                else:
                    echo_dist['reponse_status'] = 10
                    echo_dist['echo'] = "激活执行程序完成<BR>"
            else:
                # 表单错误
                echo_dist['reponse_status'] = -1
                echo_dist['echo'] = "非法执行<BR>"
        # print(echo_dist)
        from models.public.headers_model import DateEncoder
        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        # self.write(json.dumps(echo_dist))
        self.finish()