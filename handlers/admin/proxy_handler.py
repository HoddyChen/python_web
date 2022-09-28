#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import ProxyForm
from models.public.headers_model import Headers_Models
from models.user.proxy_order_model import ProxyOrderModel
import json
import logging

logger = logging.getLogger('Main')
class ProxyHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME
        if self.session['ManagerUid'] == None:
            # 退出
            # yield self.render("user/login.html", page_main=page_main)
            yield self.render("admin/login.html", page_main=page_main)
            return
        else:
            F = ProxyForm(self.request.arguments)
            if F.validate():
                # cookie_dist = self.getCookie()
                # page_main.update(cookie_dist)
                page_main['prc_type'] = F.fx_type.data
                page_main['time_type'] = F.time_type.data
                page_main['account'] = F.account.data
                page_main['uid'] = F.uid.data

                if F.fx_type.data == "list_proxy_order":
                    # 列表
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("佣金列表")
                    page_main['th_num'] = 3
                    yield self.render("admin/index_proxy_order_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proxy_order_count":
                    # 列表
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("佣金统计")
                    page_main['th_num'] = 3
                    yield self.render("admin/index_proxy_order_count_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proxy_order_count_all":
                    # 代理佣金列表
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("返佣统计")
                    page_main['th_num'] = 6
                    yield self.render("admin/index_proxy_order_count_list_all.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_settlement":
                    # 结算列表
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("结算列表")
                    page_main['th_num'] = 4
                    yield self.render("admin/index_proxy_settlement_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "add_settlement":
                    # 新增结算
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("新增结算")
                    page_main['th_num'] = 3
                    yield self.render("admin/index_proxy_add_settlement.html", page_main=page_main, session=self.session)
                    return
                else:
                    page_main['title_type'] = self.locale.translate("瑞讯银行瑞士账户申请")
                    # page_main['th_num'] = 2
                    yield self.render('admin/index_swissquote_open.html', page_main=page_main, session=self.session)
                    return
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                logger.error(get_ErrorForm(F))
                self.render('user/500.html')
                return
        self.finish()

    @gen.coroutine
    def post(self):
        echo_dist = {}
        echo_dist['data'] = []
        echo_dist["recordsTotal"] = 0
        echo_dist["recordsFiltered"] = 0
        if self.session['ManagerUid'] == None:
            # 退出
            echo_dist['reponse_status'] = -1
        else:
            # print("SS:", self.request.arguments)
            F = ProxyForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                echo_dist['reponse_status'] = 5
                P = ProxyOrderModel()
                cookie_dist = self.getCookie(1)
                page_papa = {}
                page_papa['start'] = F.start.data
                page_papa['length'] = F.length.data
                page_papa['search'] = self.get_argument('search[value]', '0')
                # page_papa['search_regex'] = F.search_regex.data
                # page_papa['page_num'] = self.get_argument('page_num', 10)
                page_papa['fx_type'] = F.fx_type.data
                page_papa['account'] = F.account.data
                page_papa['uid'] = F.uid.data

                page_papa['time_type'] = F.time_type.data
                echo_dist['fx_type'] = F.fx_type.data
                if F.fx_type.data == "list_proxy_order":
                    # 单个账户佣金列表
                    echo_dist['data'] = yield P.getProxyOrderList(page_papa['uid'], page_papa)
                elif F.fx_type.data == "list_proxy_count2":
                    # 单个账户返佣总金额
                    echo_dist['data'] = yield P.getProxyCount2(page_papa['uid'], page_papa)
                elif F.fx_type.data == "list_proxy_count":
                    # 返佣总金额
                    echo_dist['data'] = yield P.getProxyCount(page_papa['uid'], page_papa)
                elif F.fx_type.data == "list_proxy_count_all":
                    # 所有代理返佣总金额
                    echo_dist['data'] = yield P.getProxyCountAll(page_papa)
                elif F.fx_type.data == "list_proxy_order_count":
                    # 统计各账户的返佣金额
                    echo_dist['data'] = yield P.getProxyOrderCountList(page_papa['uid'], page_papa)
                elif F.fx_type.data == "list_proxy_order_count_all":
                    # 统计各代理的返佣金额
                    echo_dist['data'] = yield P.getProxyOrderCountListAll(page_papa)
                elif F.fx_type.data == "list_settlement":
                    # 统计返佣结算金额列表
                    echo_dist['data'] = yield P.getProxySettlementList(page_papa['uid'], page_papa)
                elif F.fx_type.data == "list_settlement_count":
                    # 统计结算金额
                    echo_dist['data'] = yield P.getProxySettlementCount(page_papa['uid'], page_papa)
                elif F.fx_type.data == "list_proxy_settlement_count":
                    # 统计总佣金和总结算金额
                    echo_dist['all_proxy_profit'], echo_dist['all_profit'], echo_dist['all_amount'] = yield P.getProxySettlementAllCount(page_papa['uid'])
                    data = yield P.CheckProxyInfo(page_papa['uid'])
                    if len(data) > 0:
                        echo_dist['uname'] = data[0]['uname']
                        echo_dist['iban'] = data[0]['iban']
                        echo_dist['flag'] = data[0]['flag']
                    else:
                        echo_dist['uname'] = ""
                        echo_dist['iban'] = ""
                        echo_dist['flag'] = 0
                    echo_dist['reponse_status'] = 5
                    echo_dist['echo'] = ""
                elif F.fx_type.data == "add_settlement":
                    # 新增结算金额
                    page_papa['in_uname'] = F.in_uname.data
                    page_papa['in_iban'] = F.in_iban.data
                    page_papa['out_iban'] = F.out_iban.data
                    page_papa['amount'] = F.amount.data
                    page_papa['remarks'] = F.remarks.data
                    add_flag = yield P.addProxySettlement(page_papa['uid'], page_papa)
                    if add_flag == True:
                        sendfalg = yield self.ProxySendMail(page_papa['uid'], page_papa['amount'])
                        if sendfalg == True:
                            echo_dist['reponse_status'] = 5
                            echo_dist['echo'] = "新增完成,邮件发送成功！"
                        else:
                            echo_dist['reponse_status'] = -2
                            echo_dist['echo'] = "新增完成,邮件发送失败"
                    else:
                        echo_dist['echo'] = "新增失败"
                        echo_dist['reponse_status'] = -1
                else:
                    echo_dist['echo'] = self.locale.translate("无数据")
                    echo_dist['reponse_status'] = 5
                # print(echo_dist['data'])
                if len(echo_dist.get('data')) > 0:
                    if 'allnum' in echo_dist['data'][-1]:
                        allnum = echo_dist['data'].pop()
                        # print('allnum', allnum)
                        echo_dist["recordsTotal"] = allnum['allnum']
                        echo_dist["recordsFiltered"] = allnum['allnum']
                        # s_data.pop()
                else:
                    echo_dist['echo'] = self.locale.translate("无数据")
                    echo_dist['reponse_status'] = 5
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
        # print(echo_dist)
        from models.public.headers_model import DateEncoder
        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        # self.write(json.dumps(echo_dist))
        self.finish()

    def timeType(self, time_type):
        if time_type == "the_day":
            return self.locale.translate('今日')
        elif time_type == "recent_day":
            return self.locale.translate('近一日')
        elif time_type == "the_week":
            return self.locale.translate('本周')
        elif time_type == "recent_week":
            return self.locale.translate('近一周')
        elif time_type == "the_month":
            return self.locale.translate('本月')
        elif time_type == "recent_month":
            return self.locale.translate('近一个月')
        elif time_type == "recent_month3":
            return self.locale.translate('近三个月')
        elif time_type == "recent_month6":
            return self.locale.translate('近六个月')
        elif time_type == "the_year":
            return self.locale.translate('今年')
        elif time_type == "last_year":
            return self.locale.translate('去年')
        elif time_type == "recent_year":
            return self.locale.translate('近一年')
        else:
            return self.locale.translate('全部')

    @gen.coroutine
    def ProxySendMail(self, uid, amount):
        from models.admin.admin_model import ManagerModel
        M = ManagerModel()
        uemail = yield M.getUmail(uid)
        from models.user.sendmail_model import SendmailModel
        S = SendmailModel()
        mail_text = "亲，瑞讯银行返佣" + str(amount) + "$将在下一个工作日汇入您指定账号，请查收！"
        mail_text = mail_text + self.locale.translate("来自[FXCNS邮件发送系统]")
        tomail = []
        tomail.append(uemail)
        send_flag = yield S.email_send_proxy(tomail, mail_text, self.locale.translate("瑞讯银行返佣发放通知"), "FXCNS邮件发送系统")
        if send_flag == True:
            return True
        else:
            return False # 发送失败