#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import AccountsForm
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel
from models.user.accounts_model import AccountsModel
from models.user.strategy_model import StrategyModel
import json
import logging

logger = logging.getLogger('Main')
class AccountsHandler(SessionHandler, BaseHandler):

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
            F = AccountsForm(self.request.arguments)
            # print(F.fx_type.data)
            if F.validate():
                page_main['prc_type'] = F.fx_type.data
                cookie_dist = self.getCookie()
                page_main.update(cookie_dist)
                if F.fx_type.data == "list_pricing":
                    # 列出所有的价格列表
                    page_main['title_type'] = self.locale.translate("我要续费")
                    A = AccountsModel()
                    page_main['data'] = yield A.getProductInfoList(config.PID)
                    yield self.render("user/index_pricing_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "buy_price_one":
                    # 购买订单
                    page_main['title_type'] = self.locale.translate("我要续费")
                    page_main['fx_id'] = F.fx_id.data
                    A = AccountsModel()
                    page_main['data'] = yield A.getProductInfo(F.fx_id.data)
                    yield self.render("user/index_buy2.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_account_order":
                    page_main['th_num'] = 9
                    page_main['title_type'] = self.locale.translate("购买记录")
                    page_main['fx_id'] = 9 if F.fx_id.data == None else F.fx_id.data
                    R = RedisClass()
                    endtime = R.RH.get(config.redis_ua_pid_endtime + cookie_dist["current_strategy"])
                    if endtime == None :
                        endtime = 0
                    import time
                    page_main['endtime'] = time.strftime("%Y-%m-%d", time.localtime(int(
                        float(endtime))))
                    yield self.render("user/index_account_order_list.html", page_main=page_main, session=self.session)
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
        if self.session['web_uid'] == None:
            # 退出
            echo_dist['reponse_status'] = -1
        else:
            F = AccountsForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                page_papa = {}
                # page_papa['start'] = F.start.data
                echo_dist['reponse_status'] = 5
                # S = StrategyModel()
                cookie_dist = self.getCookie(1)
                A = AccountsModel()
                if F.fx_type.data == "get_cny":
                    # 获得人民币价格
                    echo_dist['data'] = yield A.getCNY()
                elif F.fx_type.data == "buy_form":
                    cookie_dist = self.getCookie()
                    page_papa.update(cookie_dist)
                    page_papa['lang'] = self.get_lang()
                    page_papa['title_type'] = self.locale.translate("我要支付")
                    page_papa['piid'] = F.fx_id.data
                    page_papa['PaymentTypes'] = F.fx_id2.data
                    page_papa['cnh'] = F.cnh.data
                    page_papa['fx_num'] = F.fx_num.data
                    page_papa['daytype'] = F.daytype.data
                    page_papa['datetype'] = F.datetype.data
                    data_pi = yield A.getProductInfo(page_papa['piid'])
                    # print(data_pi)
                    if page_papa['daytype'] == 1:
                        page_papa['day_num'] = 30
                        page_papa['pay_cnh_num'] = self.compute_num(data_pi['info1'], page_papa['fx_num'], page_papa['cnh'], 1)
                        page_papa['pay_usd_num'] = self.compute_num(data_pi['info1'], page_papa['fx_num'], 1, 1)
                    elif page_papa['daytype'] == 2:
                        page_papa['day_num'] = 90
                        page_papa['pay_cnh_num'] = self.compute_num(data_pi['info2'], page_papa['fx_num'], page_papa['cnh'], 3)
                        page_papa['pay_usd_num'] = self.compute_num(data_pi['info2'], page_papa['fx_num'], 1, 3)
                    elif page_papa['daytype'] == 3:
                        page_papa['day_num'] = 365
                        page_papa['pay_cnh_num'] = self.compute_num(data_pi['info3'], page_papa['fx_num'], page_papa['cnh'], 12)
                        page_papa['pay_usd_num'] = self.compute_num(data_pi['info3'], page_papa['fx_num'], 1, 12)
                    else:
                        page_papa['day_num'] = 0
                        page_papa['pay_cnh_num'] = 0
                        page_papa['pay_usd_num'] = 0
                        self.redirect("/error")
                        return
                    # 增加支付订单
                    echo_dist['data'], echo_dist['OrderNo'] = yield A.setOrderTwo(page_papa, self.session['web_uid'], config.PID, cookie_dist["current_strategy"])
                    # if echo_dist['data'] == 1:
                    # 构造支付API的数据，转向支付接口
                    yield self.render("user/index_buy_pay.html", echo_dist=echo_dist, page_main=page_papa, session=self.session)
                    return
                elif F.fx_type.data == "get_account_order":
                    page_papa['fx_id'] = F.fx_id.data
                    page_papa['start'] = F.start.data
                    page_papa['length'] = F.length.data
                    echo_dist['data'] = yield A.getAccountsOrderList(cookie_dist["current_strategy"], page_papa)
                    echo_dist["recordsTotal"] = 0
                    echo_dist["recordsFiltered"] = 0
                elif F.fx_type.data == "send_pay":
                    page_papa['cnh'] = F.cnh.data
                    page_papa['fx_num'] = F.fx_num.data
                    page_papa['day_num'] = F.fx_id.data
                    page_papa['fx_no'] = F.fx_no.data
                    page_papa['PaymentTypes'] = F.fx_id2.data
                    if page_papa['PaymentTypes'] == 1:
                        page_papa['PaymentTypes'] = "支付宝"
                    else:
                        page_papa['PaymentTypes'] = "微信"
                    str_pay = ";支付方式：" + page_papa['PaymentTypes'] + ";金额：" + str(page_papa['cnh']) + ";账户数：" + str(page_papa['fx_num']) \
                              + ";购买时长：" + str(page_papa['day_num']) + "天"

                    flag = yield A.send_pay_email(str_pay, page_papa['fx_no'])
                    echo_dist['data'] = ['1']
                    echo_dist['echo'] = flag

                if echo_dist.get('data') != None:
                    if len(echo_dist.get('data')) > 1:
                        if 'allnum' in echo_dist['data'][-1]:#
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

    def compute_num(self, info, fx_num, cnh, month):
        # info_float = "%.2f" % float(info)
        cnh_str = "%.2f" % (float(info) * float(cnh) * month)
        return "%.2f" % (float(cnh_str) * fx_num)

