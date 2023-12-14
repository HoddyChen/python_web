#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import ProposalForm
from models.user.command_model import CommcandModel
import json
import logging

logger = logging.getLogger('Main')
class CommandHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        self.render('user/500.html')
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
            F = ProposalForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                echo_dist['reponse_status'] = 5
                cookie_dist = self.getCookie(1)
                C = CommcandModel()
                if F.fx_type.data == "click_margin":
                    # 一键补仓
                    # yield C.setMarginCommcand(int(F.fx_id.data), int(cookie_dist["current_strategy"]), "MakeUpOrder")
                    yield C.setNewMarginCommcand(int(F.fx_id.data), int(cookie_dist["current_strategy"]), "MakeUpOrder")
                    echo_dist['echo'] = "OK"
                elif F.fx_type.data == "click_margin_price_priority":
                    # 一键补仓
                    # yield C.setMarginCommcand(int(F.fx_id.data), int(cookie_dist["current_strategy"]), "MakeUpOrder")
                    yield C.setNewMarginCommcand(int(F.fx_id.data), int(cookie_dist["current_strategy"]), "MakeUpPriceOrder")
                    echo_dist['echo'] = "OK"
                else:
                    echo_dist['echo'] = ""
                    echo_dist['reponse_status'] = -1
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