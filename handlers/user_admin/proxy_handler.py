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
        if self.session['web_uid'] == None:
            # 退出
            # yield self.render("user/login.html", page_main=page_main)
            yield self.redirect("/user/index")
            return
        else:
            F = ProxyForm(self.request.arguments)
            if F.validate():
                P = ProxyOrderModel()
                cookie_dist = self.getCookie()
                page_main.update(cookie_dist)
                page_main['prc_type'] = F.fx_type.data
                page_main['time_type'] = F.time_type.data
                page_main['account'] = F.account.data
                page_main['gid'] = F.gid.data
                if F.fx_type.data == "list_proxy_order":
                    # 列表
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("佣金列表")
                    page_main['th_num'] = 3
                    yield self.render("user/index_proxy_order_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proxy_order_count":
                    # 列表
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("佣金统计")
                    page_main['th_num'] = 3
                    page_main['pa_class'], count_num = yield P.getProxyAccountListClassAll(self.session['web_uid'])
                    yield self.render("user/index_proxy_order_count_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_settlement":
                    # 结算列表
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("结算列表")
                    page_main['th_num'] = 4
                    yield self.render("user/index_proxy_settlement_list.html", page_main=page_main, session=self.session)
                    return
                else:
                    page_main['title_type'] = self.locale.translate("瑞讯银行瑞士账户申请")
                    # page_main['th_num'] = 2
                    yield self.render('user/index_swissquote_open.html', page_main=page_main, session=self.session)
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
        if self.session['web_uid'] == None:
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
                page_papa['gid'] = F.gid.data
                page_papa['time_type'] = F.time_type.data
                echo_dist['fx_type'] = F.fx_type.data
                if F.fx_type.data == "list_proposal":
                    echo_dist['data'] = yield P.getCsList(self.session['web_uid'], F.start.data, F.length.data)
                elif F.fx_type.data == "list_proxy_order":
                    # 单个账户佣金列表
                    echo_dist['data'] = yield P.getProxyOrderList(self.session['web_uid'], page_papa)
                elif F.fx_type.data == "list_proxy_count2":
                    # 单个账户返点总金额
                    echo_dist['data'] = yield P.getProxyCount2(self.session['web_uid'], page_papa)
                elif F.fx_type.data == "list_proxy_count":
                    # 返点总金额
                    echo_dist['data'] = yield P.getProxyCount(self.session['web_uid'], page_papa)
                elif F.fx_type.data == "list_proxy_order_count":
                    # 统计各账户的返点金额
                    echo_dist['data'] = yield P.getProxyOrderCountList(self.session['web_uid'], page_papa)
                elif F.fx_type.data == "list_settlement":
                    # 统计返点结算金额列表
                    echo_dist['data'] = yield P.getProxySettlementList(self.session['web_uid'], page_papa)
                elif F.fx_type.data == "list_settlement_count":
                    # 统计结算金额
                    echo_dist['data'] = yield P.getProxySettlementCount(self.session['web_uid'], page_papa)
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