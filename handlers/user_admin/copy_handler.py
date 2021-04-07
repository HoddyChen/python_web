#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import CopySelectForm
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel
from models.user.strategy_model import StrategyModel
import json
import re
import logging

logger = logging.getLogger('Main')
class CopyHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        echo_dist = {}
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME
        if self.session['web_uid'] == None:
            yield self.redirect("/index")
            return
        else:
            F = CopySelectForm(self.request.arguments)
            # print(F.fx_type.data)
            if F.validate():
                page_main['prc_type'] = F.fx_type.data
                page_main['time_type'] = F.time_type.data
                page_main['fx_flag'] = 9 if F.fx_flag.data == None else F.fx_flag.data
                cookie_dist = self.getCookie()
                page_main.update(cookie_dist)
                if F.fx_type.data == "list_loging":
                    # 列出所有的账号 的在线情况
                    page_main['title_type'] = self.locale.translate("在线状态")
                    page_main['fx_flag_text1'] = self.locale.translate("已授权")
                    page_main['fx_flag_text0'] = self.locale.translate("未授权")
                    page_main['th_num'] = 3
                    yield self.render("user/index_copy_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_position":
                    # 持仓统计
                    page_main['title_type'] = self.locale.translate("持仓监控")
                    page_main['th_num'] = 10
                    yield self.render("user/index_position_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_account":
                    # 账户管理
                    # print("ip:",self.ip)
                    # self.get_user_ip()
                    page_main['title_type'] = self.locale.translate("账户管理")
                    page_main['th_num'] = 6
                    R = RedisClass()
                    endtime = None#R.RH.get(config.redis_ua_pid_endtime + cookie_dist["current_strategy"])
                    import time
                    # print(endtime)
                    if endtime == None or endtime == "null":
                        M = MasterModel()
                        mdata = yield M.getMaterInfo(cookie_dist["current_strategy"], config.PID)
                        # print(mdata)
                        if mdata['endtime'] == None:
                            page_main['endtime'] = "1970-01-01"
                        else:
                            # page_main['endtime'] = time.strftime("%Y-%m-%d", mdata['endtime'])
                            page_main['endtime'] = mdata['endtime'].strftime("%Y-%m-%d")
                    else:
                        page_main['endtime'] = time.strftime("%Y-%m-%d", time.localtime(int(float(endtime))))
                    yield self.render("user/index_account_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_net_ratio":
                    # 资料风控
                    page_main['title_type'] = self.locale.translate("账户资金")
                    page_main['th_num'] = 8
                    yield self.render("user/index_net_ratio_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_order_count":
                    # 统计手数与单量
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("订单统计")
                    page_main['th_num'] = 8
                    yield self.render("user/index_order_count_list.html", page_main=page_main, session=self.session)
                    return
                else:
                    yield self.redirect("/index")
                    return

            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
                self.redirect("/index")
                return


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
            # print(self.request.arguments)
            F = CopySelectForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                cookie_dist = self.getCookie(1)
                page_papa = {}
                page_papa['start'] = F.start.data
                page_papa['length'] = F.length.data
                page_papa['search'] = self.get_argument('search[value]', '0')
                # page_papa['search_regex'] = F.search_regex.data
                # page_papa['page_num'] = self.get_argument('page_num', 10)
                page_papa['fx_type'] = F.fx_type.data
                page_papa['fx_flag'] = F.fx_flag.data
                page_papa['time_type'] = F.time_type.data
                echo_dist['fx_type'] = F.fx_type.data
                if self.chick_seach(page_papa['search']):

                    S = StrategyModel()
                    if F.fx_type.data == "list_loging":
                        # 列出所有的账号 的在线情况
                        echo_dist['data'] = yield S.getStrategyLoging(cookie_dist["current_strategy"], page_papa)
                    elif F.fx_type.data == "list_position":
                        # 列出持仓个数及资金情况
                        echo_dist['data'] = yield S.getStrategyPositionList(cookie_dist["current_strategy"], page_papa)
                    elif F.fx_type.data == "list_account":
                        # 账户管理
                        echo_dist['data'] = yield S.getCopyList(cookie_dist["current_strategy"], page_papa)
                    elif F.fx_type.data == "list_net_ratio":
                        # 账户资金
                        echo_dist['data'] = yield S.getCopyNetRatioList(cookie_dist["current_strategy"], page_papa)
                    elif F.fx_type.data == "list_order_count":
                        # 统计手数与单量
                        echo_dist['data'] = yield S.getCopyOrderCountList(cookie_dist["current_strategy"], page_papa)
                    else:
                        echo_dist['data'] = []
                    if len(echo_dist.get('data')) > 0:
                        if 'allnum' in echo_dist['data'][-1]:
                            allnum = echo_dist['data'].pop()
                            logger.debug(allnum)
                            echo_dist["recordsTotal"] = allnum['allnum']
                            echo_dist["recordsFiltered"] = allnum['allnum']
                            # s_data.pop()
                    else:
                        echo_dist['echo'] = self.locale.translate("无数据")
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
        par = r'^\+?[1-9][0-9]*$'
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
        else:
            return self.locale.translate('全部')