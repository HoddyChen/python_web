# coding = utf-8
#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import LoginForm
from models.admin.admin_model import ManagerModel
import json
import logging
from models.public.confrom_model import AccountsForm
from models.user.accounts_model import AccountsModel
from models.admin.pay_model import PayModel

logger = logging.getLogger('Main')
class PayOrderHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        # print(self.request.host)
        # tornado.locale.set_default_locale("en_US")
        echo_dist = {}
        page_main = {}
        page_main['title_website'] = config.WEBSITE_NAME + "管理区"
        if self.session['ManagerUid'] == None:
            yield self.render("admin/login.html", page_main=page_main)
            return
        else:
            F = AccountsForm(self.request.arguments)
            # print(F.fx_type.data)
            if F.validate():
                page_main['prc_type'] = F.fx_type.data
                # cookie_dist = self.getCookie()
                # page_main.update(cookie_dist)
                if F.fx_type.data == "list_pricing":
                    # 列出所有的价格列表
                    page_main['title_type'] = "Price List"
                    A = AccountsModel()
                    page_main['data'] = yield A.getProductInfoList(config.PID)
                    yield self.render("admin/index_pricing_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_account_order":
                    page_main['th_num'] = 12
                    page_main['title_type'] = "List Order"
                    page_main['fx_id'] = 9 if F.fx_id.data == None else F.fx_id.data
                    yield self.render("admin/index_account_order_list.html", page_main=page_main, session=self.session)
                    return
                else:
                    self.redirect("/index")
                    return

            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                logger.debug(echo_dist['echo'])
                echo_dist['reponse_status'] = 1
                self.redirect("/index")
                return

    @gen.coroutine
    def post(self):
        echo_dist = {}
        page_main = {}
        page_main['title_website'] = config.WEBSITE_NAME + "管理区"
        if self.session['ManagerUid'] == None:
            yield self.render("admin/login.html", page_main=page_main)
            return
        else:
            #登陆
            F = AccountsForm(self.request.arguments)
            if F.validate():  # and F.cla.data == "SendError"
                page_papa = {}
                # page_papa['start'] = F.start.data
                echo_dist['reponse_status'] = 5
                P = PayModel()
                if F.fx_type.data == "get_account_order":
                    # 获得支付订单列表
                    page_papa['fx_id'] = F.fx_id.data
                    page_papa['start'] = F.start.data
                    page_papa['length'] = F.length.data
                    page_papa['search'] = self.get_argument('search[value]', "0")
                    echo_dist['data'] = yield P.getPayOrderList(page_papa)
                    echo_dist["recordsTotal"] = 0
                    echo_dist["recordsFiltered"] = 0
                elif F.fx_type.data == "set_pay":
                    # 更新支付状态
                    oid = F.fx_id.data
                    otype = F.fx_id2.data
                    flag, email = yield P.setPayOrder(oid, otype)
                    mail_flag = ""
                    if flag == 1 and otype == 1:
                        from models.user.sendmail_model import SendmailModel
                        S = SendmailModel()
                        email_list = []
                        email_list.append(email)
                        to_text = """很高兴的通知您，您的支付订单已经处理完成，将在5分钟内同步至所有服务器。<BR>
                        感谢您的支持，如有什么疑问都可以直接回复此邮件"""
                        to_title = "订单支付成功"
                        mail_flag = yield S.email_send(email_list, to_text, to_title)
                    echo_dist['data'] = ['1']
                    echo_dist['echo'] = str(flag) + "," + str(mail_flag)

                if echo_dist.get('data') != None:
                    if len(echo_dist.get('data')) > 1:
                        if 'allnum' in echo_dist['data'][-1]:  #
                            allnum = echo_dist['data'].pop()
                            logger.debug(allnum)
                            echo_dist["recordsTotal"] = allnum['allnum']
                            echo_dist["recordsFiltered"] = allnum['allnum']
                            # s_data.pop()
                else:
                    echo_dist['echo'] = self.locale.translate("无数据")
                    echo_dist['reponse_status'] = 5
                    echo_dist['data'] = []
                # echo_dist['data'] = s_data
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
        from models.public.headers_model import DateEncoder
        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        # self.write(json.dumps(echo_dist))
        self.finish()