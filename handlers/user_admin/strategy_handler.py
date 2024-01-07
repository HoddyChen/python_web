#coding=utf-8
import tornado
import json
import logging
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import AccountsForm
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel
from models.user.strategy_model import StrategyModel
from models.user.order_model import OrderModel


logger = logging.getLogger('Main')
class StrategyHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        echo_dist = {}
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME
        if self.session['web_uid'] == None:
            # self.redirect("/index")
            echo_dist['reponse_status'] = -1
        else:
            cookie_dist = self.getCookie()
            if cookie_dist['current_strategy'] == None:
                echo_dist['reponse_status'] = -1
            else:
                F = AccountsForm(self.request.arguments)
                # print(F.fx_type.data)
                if F.validate():
                    echo_dist['reponse_status'] = 5
                    # logger.debug(F.fx_type.data)
                    # logger.debug(self.get_secure_cookie("current_strategy"))
                    if F.fx_type.data == "list":
                        # 列出所有策略的账号并返回
                        S = StrategyModel()
                        s_data = yield S.getStrategyList(self.session['web_uid'])
                        if len(s_data) == 0:
                            echo_dist['reponse_status'] = 0
                        else:
                            echo_dist['s_data'] = s_data
                            # print(s_data)
                            if len(s_data) == 1:
                                self.set_secure_cookie("current_strategy" + self.session['web_uid'], str(s_data[0]['uaid']))
                                self.set_secure_cookie("current_ma_name" + self.session['web_uid'], "null" if s_data[0]['ma_name'] == None else s_data[0]['ma_name'])
                                self.set_secure_cookie("current_account" + self.session['web_uid'], "null" if s_data[0]['account'] == None else s_data[0]['account'])
                                self.set_secure_cookie("current_key_ma" + self.session['web_uid'], "null" if s_data[0]['key_ma'] == None else s_data[0]['key_ma'])
                                self.set_secure_cookie("current_logo_url" + self.session['web_uid'],
                                                       "null" if s_data[0]['logo_url'] == None else s_data[0]['logo_url'])
                                echo_dist['strategy'] = str(s_data[0]['uaid'])
                            else:
                                echo_dist['strategy'] = cookie_dist['current_strategy']
                            # 策略详情,包括到期时间，可用账户数量
                            M = MasterModel()
                            # 获得购买授权数量
                            echo_dist['master_max_num'] = yield M.getMaterCopyNum(51, echo_dist['strategy'])
                            # 获取 已用授权和总接入数量
                            master_count_list = yield M.getMaterCopyCount(echo_dist['strategy'])
                            echo_dist['master_count_all'] = 0
                            echo_dist['master_count_ok'] = 0
                            if len(master_count_list) > 0:
                                for master_count in master_count_list:
                                    if master_count['follow_flag'] == 1:
                                        echo_dist['master_count_ok'] = master_count['follow_num']
                                    echo_dist['master_count_all'] = echo_dist['master_count_all'] + master_count['follow_num']
                    elif F.fx_type.data == "list_master":
                        # 列出所有策略的账号并返回
                        page_main.update(cookie_dist)
                        page_main['th_num'] = 4
                        page_main['title_type'] = self.locale.translate("编辑策略列表")
                        yield self.render("user/index_master_list.html", page_main=page_main, session=self.session)
                        return

                    elif F.fx_type.data == "count":
                        # 策略资金统计
                        S = StrategyModel()
                        echo_dist['echo'] = yield S.getStrategyCount(cookie_dist['current_strategy'])
                        if echo_dist['echo'] == None:
                            echo_dist['reponse_status'] = 0
                    elif F.fx_type.data == "symbol_count":
                        # 主策略的持仓品种统计
                        S = StrategyModel()
                        echo_dist["symbol_list"], echo_dist["num_list"] = yield S.getStrategySymbol(cookie_dist['current_strategy'])
                        if echo_dist['symbol_list'] == None or echo_dist['num_list'] == None:
                            echo_dist['reponse_status'] = 0
                    elif F.fx_type.data == "loging_count":
                        # 在线状态统计
                        S = StrategyModel()
                        echo_dist["loging_data"] = yield S.getStrategyLogingStatus(cookie_dist['current_strategy'])

                    elif F.fx_type.data == "position_count":
                        # 持仓一致性统计
                        S = StrategyModel()
                        echo_dist["position_count_data"] = yield S.getStrategyPositionCount(cookie_dist['current_strategy'])
                    elif F.fx_type.data == "net_ratio_list":
                        # 已用保证金/净值的比例
                        S = StrategyModel()
                        echo_dist["echo"], echo_dist["m_echo"] = yield S.getStrategyPositionRatio(cookie_dist['current_strategy'])
                        if echo_dist["m_echo"] == None:
                            echo_dist['reponse_status'] = 0
                    elif F.fx_type.data == "master_max_num":
                        # 策略详情,包括到期时间，可用账户数量
                        M = MasterModel()
                        # 获得购买授权数量
                        echo_dist['master_max_num'] = yield M.getMaterCopyNum(51, cookie_dist['current_strategy'])
                        # 获取 已用授权和总接入数量
                        master_count_list = yield M.getMaterCopyCount(cookie_dist['current_strategy'])
                        echo_dist['master_count_all'] = 0
                        echo_dist['master_count_ok'] = 0
                        if len(master_count_list) > 0:
                            for master_count in master_count_list:
                                if master_count['follow_flag'] == 1:
                                    echo_dist['master_count_ok'] = master_count['follow_num']
                                echo_dist['master_count_all'] = echo_dist['master_count_all'] + master_count['follow_num']
                    elif F.fx_type.data == "get_parameter":
                        S = StrategyModel()
                        row = yield S.getParameter(cookie_dist['current_strategy'], F.fx_id.data)
                        O = OrderModel()
                        echo_dist['pnum'] = yield O.get_PositionOrderNum2(cookie_dist['current_strategy'], F.fx_id.data)
                        logger.debug("get_parameter:%s" % row)
                        if row == None:
                            echo_dist['reponse_status'] = 0
                        else:
                            echo_dist.update(row)
                    else:
                        yield self.redirect("/user/index")
                        return
                else:
                    # 表单错误
                    from models.public.confrom_model import get_ErrorForm
                    echo_dist['echo'] = get_ErrorForm(F)
                    echo_dist['reponse_status'] = 1
            # print(self.request.host)
            # B  = BaseHandler()
            # tornado.locale.set_default_locale("en_US")
            # self.session["uname"] = "12345"
        logger.debug(echo_dist)
        from models.public.headers_model import DateEncoder
        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        # self.write(json.dumps(echo_dist))
        self.finish()

    @gen.coroutine
    def post(self):
        echo_dist = {}
        if self.session['web_uid'] == None:
            echo_dist['reponse_status'] = -1
        else:
            #
            F = AccountsForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                from models.user.strategy_model import StrategyModel
                S = StrategyModel()
                echo_dist['reponse_status'] = 5
                cookie_dist = self.getCookie(1)
                page_papa = {}
                page_papa['start'] = F.start.data
                page_papa['length'] = F.length.data
                page_papa['search'] = self.get_argument('search[value]', '0')
                page_papa['fx_type'] = F.fx_type.data
                page_papa['fx_id'] = F.fx_id.data
                if F.fx_type.data == "edit_authorization":
                    # 修改授权
                    R = RedisClass()
                    flag = yield S.edit_authorization(self.session['web_uid'], self.get_user_ip(), cookie_dist["current_strategy"], F.fx_id.data)
                    if flag < 0:
                        echo_dist['reponse_status'] = flag
                    else:
                        logger.debug("edit_authorization:%s,%s,%s" % (cookie_dist["current_strategy"], str(F.fx_id.data), str(flag)))
                        # R.RH.hset(config.redis_master_uaid_Hash + str(self.get_secure_cookie("current_strategy"),
                        #                                               encoding="utf-8"), str(F.fx_id.data), str(flag))
                        yield R.set_MaterFollow(cookie_dist["current_strategy"], str(F.fx_id.data), str(flag))
                        echo_dist['echo'] = flag
                elif F.fx_type.data == "list_master":
                    echo_dist['data'] = yield S.getStrategyListPage(self.session['web_uid'], page_papa, 1)
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

                elif F.fx_type.data == "click_delete":
                    echo_dist['reponse_status'] = yield S.edit_master_delete(self.session['web_uid'], self.get_user_ip(), F.fx_id.data)
                    if echo_dist['reponse_status'] != 5:
                        echo_dist['echo'] = self.locale.translate("操作失败")
                elif F.fx_type.data == "delete_follow_flag":
                    echo_dist['reponse_status'] = yield S.edit_follow_delete(cookie_dist["current_strategy"], self.session['web_uid'], self.get_user_ip(), F.fx_id.data)
                    if echo_dist['reponse_status'] != 5:
                        echo_dist['echo'] = self.locale.translate("操作失败")
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
        # from models.public.headers_model import DateEncoder
        # yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        self.write(json.dumps(echo_dist))
        self.finish()