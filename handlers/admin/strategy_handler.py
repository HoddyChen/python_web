#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import CopySelectForm
from handlers.myredis.redis_class import RedisClass
# from models.admin.master_model import MasterModel
from models.admin.strategy_model import StrategyModel
import json
import re
import logging
import time

logger = logging.getLogger('Main')
class StrategyHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        echo_dist = {}
        page_main = {}
        page_main['title_website'] = config.WEBSITE_NAME + "管理区"
        if self.session['ManagerUid'] == None:
            yield self.render("admin/login.html", page_main=page_main)
            # yield self.redirect("/adminSZba2qjbydxVhMJpuKfy/", permanent=False)
            return
        else:
            page_main['lang'] = self.get_argument('lang', "")
            prc_type = self.get_argument('prc_type', None)
            fx_type = self.get_argument('fx_type', None)
            page_main['fx_type'] = fx_type
            page_main['title_main'] = "管理区"
            page_main['title_type'] = "资讯"
            page_main['strategy_id'] = self.get_argument('strategy_id', 0)
            page_main['uaid'] = self.get_argument('uaid', 0)
            F = CopySelectForm(self.request.arguments)
            # print(F.fx_type.data)
            if F.validate():
                page_main['prc_type'] = F.fx_type.data
                page_main['time_type'] = F.time_type.data
                page_main['fx_flag'] = 9 if F.fx_flag.data == None else F.fx_flag.data
                S = StrategyModel()
                if F.fx_type.data == "list_strategy":
                    # 列出所有的账号 的在线情况
                    page_main['title_type'] = self.locale.translate("自研策略列表")
                    page_main['th_num'] = 4
                    yield self.render("admin/index_strategy_list.html", page_main=page_main, session=self.session)
                    return

                elif F.fx_type.data == "strategy_main":
                    # 自研策略面板
                    page_main['title_type'] = self.locale.translate("自研策略面板")
                    page_main['th_num'] = 5
                    page_main['SymbolNameDist'] = yield S.getStrategySymbolName(page_main)
                    yield self.render("admin/index_strategy_index.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_position":
                    # 持仓统计
                    page_main['title_type'] = self.locale.translate("持仓监控")
                    page_main['th_num'] = 10
                    yield self.render("user/index_position_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "strategy_ma":
                    # 策略均线
                    page_main['color_v'] = {"P": "#034aff", 20: "#6C6C6C", 30: "#AE0000", 60: "#00AEAE", 120: "#D200D2", 200: "#8600FF", 250: "#00AEAE",
                     360: "#F00078"}
                    page_main['title_type'] = self.locale.translate("策略均线")
                    page_main['symbol_name'] = self.get_argument('symbol_name', "")
                    page_main['time_period'] = S.time_period
                    page_main['period_v'] = yield S.getStrategySymbolMaPeriod(page_main)
                    yield self.render("admin/index_strategy_ma.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_order_count":
                    # 统计手数与单量
                    page_main['time_str'] = self.timeType(page_main['time_type'])
                    page_main['title_type'] = self.locale.translate("订单统计")
                    page_main['th_num'] = 7
                    yield self.render("admin/index_strategy_order_count.html", page_main=page_main, session=self.session)
                    return
                else:
                    yield self.redirect("adminSZba2qjbydxVhMJpuKfy/")
                    return

            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
                self.redirect("adminSZba2qjbydxVhMJpuKfy/")
                return


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
            # print(self.request.arguments)
            F = CopySelectForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                page_papa = {}
                page_papa['start'] = F.start.data
                page_papa['length'] = F.length.data
                page_papa['search'] = self.get_argument('search[value]', '0')
                page_papa['form_id'] = F.form_id.data
                # page_papa['page_num'] = self.get_argument('page_num', 10)
                page_papa['fx_type'] = F.fx_type.data
                page_papa['fx_flag'] = F.fx_flag.data
                page_papa['time_type'] = F.time_type.data
                page_papa['symbol_name'] = self.get_argument('symbol_name', "")
                page_papa['strategy_id'] = self.get_argument('strategy_id', 0)
                page_papa['uaid'] = self.get_argument('uaid', 0)
                echo_dist['fx_type'] = F.fx_type.data
                echo_dist['reponse_status'] = 0
                if self.chick_seach(page_papa['search']):

                    S = StrategyModel()
                    if F.fx_type.data == "list_strategy":
                        # 列出所有的账号 的在线情况
                        echo_dist['data'] = yield S.getStrategyLoging(page_papa)
                    elif F.fx_type.data == "count":
                        # 统计数据
                        echo_dist['echo'] = yield S.getStrategyCount(page_papa)
                    elif F.fx_type.data == "symbol_count":
                        # 主策略持仓品种统计
                        echo_dist["symbol_list"], echo_dist["num_list"] = yield S.getStrategySymbol(page_papa, False)
                    elif F.fx_type.data == "symbol_count_his":
                        # 主策略的历史品种统计
                        echo_dist["symbol_list"], echo_dist["num_list"] = yield S.getStrategySymbol(page_papa, True)
                    elif F.fx_type.data == "funds_count":
                        # 资金曲线
                        echo_dist['data'] = yield S.getFundsCount(page_papa)
                    elif F.fx_type.data == "position":
                        # 列出持仓
                        echo_dist['data'] = yield S.getStrategySymbolList(page_papa)
                    elif F.fx_type.data == "strategy_ma":
                        # 策略均线
                        echo_dist['data'], echo_dist['datas_columns'] = yield S.getStrategySymbolMa(page_papa)
                    elif F.fx_type.data == "save_period":
                        # 保存周期
                        if page_papa['form_id'] == 9588:
                            echo_dist['echo'] = yield S.setStrategyPeriod(page_papa)
                        else:
                            echo_dist['echo'] = False
                    elif F.fx_type.data == "save_open_flag":
                        # 保存货币开关
                        echo_dist['echo'] = yield S.setStrategyOpenFlag(page_papa)
                    elif F.fx_type.data == "list_order_count":
                        # 统计手数与单量
                        echo_dist['data'] = yield S.getOrderCount(page_papa)
                    elif F.fx_type.data == "getStrategy_symbol":
                        # 策略货币对参数
                        echo_dist['data'] = yield S.getStrategySymbolName(page_papa)
                    else:
                        echo_dist['echo'] = []
                    if len(echo_dist.get('data')) > 0:
                        if 'allnum' in echo_dist['data'][-1]:
                            allnum = echo_dist['data'].pop()
                            logger.debug(allnum)
                            echo_dist["recordsTotal"] = allnum['allnum']
                            echo_dist["recordsFiltered"] = allnum['allnum']
                            # s_data.pop()
                        echo_dist['reponse_status'] = 5
                    else:
                        echo_dist['data'] = []
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
        # logger.debug(echo_dist)
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