#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import ParameterForm
from models.user.user_model import UserModel
import json
import time
import logging

logger = logging.getLogger('Main')
class ParameterHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        self.write("")
        self.finish()

    @gen.coroutine
    def post(self):
        echo_dist = {}
        if self.session['web_uid'] == None:
            # 退出
            echo_dist['reponse_status'] = -1
        else:
            # print("SS:", self.request.arguments)
            F = ParameterForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                cookie_dist = self.getCookie(1)
                echo_dist['reponse_status'] = 5
                page_papa = {}
                page_papa['maxtime'] = 10 if F.maxtime.data == None else F.maxtime.data
                page_papa['maxloss'] = 10 if F.maxloss.data == None else F.maxloss.data
                page_papa['maxnum'] = 5 if F.maxnum.data == None else F.maxnum.data
                page_papa['reflex'] = 0 if F.reflex.data == None else F.reflex.data
                page_papa['fixed'] = 0 if F.fixed.data == None else F.fixed.data
                page_papa['percent'] = 0 if F.percent.data == None else F.percent.data
                page_papa['rate_min'] = 0.01 if F.rate_min.data == None else F.rate_min.data
                page_papa['rate_max'] = 0.5 if F.rate_max.data == None else F.rate_max.data
                page_papa['rate'] = 0 if F.rate.data == None else F.rate.data
                page_papa['tpsl_flag'] = 0 if F.tpsl_flag.data == None else F.tpsl_flag.data
                page_papa['pending_flag'] = 0 if F.pending_flag.data == None else F.pending_flag.data
                page_papa['allowed_sign'] = -1
                page_papa['uid'] = self.session['web_uid']
                page_papa['ip'] = self.get_user_ip()
                page_papa['balance'] = -100000
                page_papa['credit'] = -100000
                page_papa['quity'] = -100000
                page_papa['profit'] = -100000
                page_papa['margin'] = -100000
                U = UserModel()
                if F.fx_type.data == "edit":
                    #
                    from models.user.master_model import MasterModel
                    M = MasterModel()
                    m_dist = yield M.getMasterKEY(cookie_dist["current_strategy"])
                    if m_dist != None:
                        page_papa['MasterKey'] = m_dist['key_ma']
                        page_papa['pid'] = config.PID
                        # page_papa.update(m_dist)
                        page_papa['parameter_time'] = int(time.time())
                        logger.debug("BB:%s" % page_papa)
                        echo_dist['data'] = yield U.updataAccount(page_papa, F.fx_id.data)
                        if echo_dist['data'] != None:
                            # if echo_dist['data']['@flag'] == 0:
                            echo_dist['reponse_status'] = echo_dist['data']['@flag']
                            echo_dist['echo'] = self.locale.translate("保存失败！")
                        else:
                            echo_dist['reponse_status'] = -2
                            echo_dist['echo'] = self.locale.translate("跟单账户资料发生意外错误！")
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
        # from models.public.headers_model import DateEncoder
        # yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        self.write(json.dumps(echo_dist))
        self.finish()