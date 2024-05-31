#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import HistoryForm
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel
from models.user.strategy_model import StrategyModel
import json
import re
import logging

logger = logging.getLogger('Main')
class HistoryHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        echo_dist = {}
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = self.locale.translate("交易账户")
        cookie_dist = self.getCookie(1)
        F = HistoryForm(self.request.arguments)
        if F.validate():  # and F.cla.data == "SendError"

            M = MasterModel()
            S = StrategyModel()
            page_papa = {}
            page_main['urlkey'] = F.k.data
            page_main['prc_type'] = F.fx_type.data
            page_main['time_type'] = F.time_type.data
            page_main['time_str'] = self.timeType(F.time_type.data)
            pp = yield M.checkMaterAndFollow(cookie_dist["current_strategy"], F.uaid.data)
            if pp or cookie_dist["current_strategy"] == str(F.uaid.data):
                page_main['uaid'] = F.uaid.data
                s_data2 = yield S.getfollowidStrategy(cookie_dist["current_strategy"])
                page_main.update(s_data2)
            else:
            # print(F.fx_type.data)
                if F.k.data != None or F.k.data != "":
                    cookie_pass = self.get_secure_cookie('fx_url_' + F.k.data)
                    # print("cookie_pass:", cookie_pass)
                    if cookie_pass == None:
                        page_main['urlkey'] = F.k.data
                        yield self.render("user/login_url.html", page_main=page_main, session=self.session)
                        self.session['_xsrf'] = self.xsrf_token
                        return
                    else:
                        page_main['fx_pass'] = cookie_pass

                        page_main['uaid'] = self.get_secure_cookie('fx_id_' + F.k.data)

                        # 授权状态
                        s_data = yield S.getUrlStrategy(page_main['urlkey'], page_main['fx_pass'])
                        # print("s_data:",s_data)
                        if s_data == None:
                            s_data2 = yield S.getUaidStrategy(page_main['urlkey'], page_main['fx_pass'])
                            if s_data2 == None:
                                page_main['urlkey'] = F.k.data
                                page_main['echo'] = self.locale.translate("授权取消")
                                yield self.render("user/login_url.html", page_main=page_main, session=self.session)
                                self.session['_xsrf'] = self.xsrf_token
                                return
                            else:
                                page_main.update(s_data2)
                        else:
                            page_main.update(s_data)
            if F.fx_type.data == "report":
                #报告
                page_main['title_type'] = self.locale.translate("报告")
                # page_main['th_num'] = 13
                yield self.render("user/index_url_report.html", page_main=page_main, session=self.session)
                return
            elif F.fx_type.data == "history":
                #
                page_main['title_type'] = self.locale.translate("历史记录")
                page_main['th_num'] = 13
                yield self.render("user/index_url_history_list.html", page_main=page_main, session=self.session)
                return
            elif F.fx_type.data == "position":
                # 持仓
                page_main['title_type'] = self.locale.translate("持仓记录")
                page_main['th_num'] = 11
                yield self.render("user/index_url_position_list.html", page_main=page_main, session=self.session)
                return
            elif F.fx_type.data == "symbol_distributed":
                # 品种分布
                page_main['title_type'] = self.locale.translate("品种分布")
                # page_main['th_num'] = 13
                yield self.render("user/index_url_symbol_distributed.html", page_main=page_main, session=self.session)
                return
            elif F.fx_type.data == "funds_count":
                # 资金曲线
                page_main['title_type'] = self.locale.translate("利润曲线")
                # page_main['th_num'] = 13
                yield self.render("user/index_url_line_chart.html", page_main=page_main, session=self.session)
                return
            elif F.fx_type.data == "profitability":
                # 盈利能力
                page_main['title_type'] = self.locale.translate("盈利能力")
                # page_main['th_num'] = 13
                yield self.render("user/index_url_profitability.html", page_main=page_main, session=self.session)
                return
            elif F.fx_type.data == "time_sharing":
                # 分时统计
                page_main['title_type'] = self.locale.translate("盈利能力-分时统计")
                page_main['th_num'] = 8
                yield self.render("user/index_url_time_sharing_list.html", page_main=page_main, session=self.session)
                return
            elif F.fx_type.data == "list_order_count":
                # 统计手数与单量
                page_main['time_str'] = self.timeType(page_main['time_type'])
                page_main['title_type'] = self.locale.translate("订单统计")
                page_main['th_num'] = 8
                yield self.render("user/index_order_count_list.html", page_main=page_main, session=self.session)
                return
            else:
                # yield self.render("user/login_url.html", page_main=page_main, session=self.session)
                #报告
                page_main['title_type'] = self.locale.translate("报告")
                page_main['th_num'] = 13
                yield self.render("user/index_url_report.html", page_main=page_main, session=self.session)
                return

        else:
            # 表单错误
            from models.public.confrom_model import get_ErrorForm
            echo_dist['echo'] = get_ErrorForm(F)
            echo_dist['reponse_status'] = 1
            self.render("user/login_url.html", page_main=page_main, session=self.session)
            return



    @gen.coroutine
    def post(self):
        echo_dist = {}
        echo_dist['data'] = []
        echo_dist["recordsTotal"] = 0
        echo_dist["recordsFiltered"] = 0
            # print(self.request.arguments)
        open_flag = False
        cookie_dist = self.getCookie(1)
        F = HistoryForm(self.request.arguments)
        if F.validate():  # and F.cla.data == "SendError"

            M = MasterModel()
            page_papa = {}
            S = StrategyModel()
            open_flag = yield M.checkMaterAndFollow(cookie_dist["current_strategy"], F.uaid.data)
            if open_flag or cookie_dist["current_strategy"] == str(F.uaid.data):
                # 有策略登陆
                open_flag = True
                echo_dist['reponse_status'] = 5
                page_papa['uaid'] = int(F.uaid.data)
            else:
                # 通过密码登陆查看
                if F.fx_type.data == "login":
                    if tornado.escape.to_unicode(self.request.arguments['_xsrf'][0]) != self.session['_xsrf']:
                        echo_dist['echo'] = "验证失败"
                        echo_dist['reponse_status'] = 1
                    else:
                        s_data = yield S.chickUrlKey(F.k.data, F.fx_pass.data)
                        # print(s_data)
                        if s_data:
                            import time
                            self.set_secure_cookie("fx_url_" + F.k.data, F.fx_pass.data, expires=time.time()+172800)
                            self.set_secure_cookie("fx_id_" + F.k.data, str(s_data['uaid']), expires=time.time()+172800)
                            page_papa['fx_pass'] = F.fx_pass.data
                            echo_dist['reponse_status'] = 5
                        else:
                            # self.redirect("/h?k="+F.k.data)
                            echo_dist['echo'] = self.locale.translate("密码错误或不允许查看")
                            echo_dist['reponse_status'] = 1

                else:
                    fx_pass = None if self.get_secure_cookie('fx_url_' + F.k.data) == None else str(self.get_secure_cookie('fx_url_' + F.k.data), encoding="utf-8")
                    if fx_pass:
                        page_papa['uaid'] = int(self.get_secure_cookie('fx_id_' + F.k.data))
                    else:
                        self.redirect("/h?k="+F.k.data)
                        return
            page_papa['urlkey'] = F.k.data
            page_papa['start'] = F.start.data
            page_papa['length'] = F.length.data
            page_papa['search'] = self.get_argument('search[value]', '0')
            # page_papa['search_regex'] = F.search_regex.data
            # page_papa['page_num'] = self.get_argument('page_num', 10)
            page_papa['fx_type'] = F.fx_type.data
            page_papa['time_type'] = F.time_type.data
            page_papa['time_str'] = self.timeType(F.time_type.data)
            if self.chick_seach(page_papa['search']):
                if F.fx_type.data == "report":
                    # 总报告
                    echo_dist['data'] = yield S.getHistoryReportCount(page_papa)
                elif F.fx_type.data == "history":
                    # 列出账号 的历史
                    echo_dist['data'] = yield S.getHistoryOrderList(page_papa)
                elif F.fx_type.data == "position":
                    # 列出持仓
                    echo_dist['data'] = yield S.getPositionOrderList(page_papa)
                elif F.fx_type.data == "position_count":
                    # 账户资金
                    echo_dist['data'] = yield S.getPositionCount(page_papa)
                elif F.fx_type.data == "history_count":
                    # 统计手数与单量
                    echo_dist['data'] = yield S.getHistoryCount(page_papa)
                elif F.fx_type.data == "symbol_distributed":
                    # 品种分布
                    echo_dist['data'] = yield S.getDistributedSymbol(page_papa)
                elif F.fx_type.data == "funds_count":
                    # 资金曲线
                    echo_dist['data'] = yield S.getFundsCount(page_papa)
                elif F.fx_type.data == "profitability":
                    # 盈利能力
                    echo_dist['data'] = yield S.getProfitability(page_papa)
                elif F.fx_type.data == "time_sharing":
                    # 盈利能力-分时统计
                    echo_dist['data'] = yield S.getTimeSharing(page_papa)
                elif F.fx_type.data == "exit_out":
                    # 退出
                    # self.clear_all_cookies()
                    self.clear_cookie('fx_url_' + F.k.data)
                else:
                    echo_dist['data'] = []
                if len(echo_dist.get('data')) > 0:
                    if 'allnum' in echo_dist['data'][-1]:
                        allnum = echo_dist['data'].pop()
                        logger.debug(allnum)
                        echo_dist["recordsTotal"] = allnum['allnum']
                        echo_dist["recordsFiltered"] = allnum['allnum']
                    echo_dist['reponse_status'] = 5
                        # s_data.pop()
                else:
                    echo_dist['echo'] = self.locale.translate("请......")
                    echo_dist['reponse_status'] = 5
                # echo_dist['data'] = s_data
            else:
                echo_dist['echo'] = self.locale.translate("搜索内容只能是全数字的账户")
                echo_dist['reponse_status'] = 1
        else:
            # 表单错误
            from models.public.confrom_model import get_ErrorForm
            echo_dist['echo'] = get_ErrorForm(F)
            echo_dist['reponse_status'] = 1
        logger.debug(echo_dist)
        from models.public.headers_model import DateEncoder
        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        # self.write(json.dumps(echo_dist))
        self.finish()

    def chick_seach(self, val):
        par = r'^\+?[a-zA-Z\d]*$'
        if re.match(par, val) or val == "0" or val == "":
            logger.debug("true")
            return True
        else:
            logger.debug("chick_seach:", val)
            return False

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
        elif time_type == "year":
            return self.locale.translate('按年')
        elif time_type == "month":
            return self.locale.translate('按月')
        elif time_type == "week":
            return self.locale.translate('按周')
        elif time_type == "day":
            return self.locale.translate('按天')
        else:
            return self.locale.translate('全部')