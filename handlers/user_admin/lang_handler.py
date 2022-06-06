#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import StrategyForm
from models.public.confrom_model import InfoForm
from handlers.myredis.redis_class import RedisClass
from models.user.user_model import UserModel
from models.user.strategy_model import StrategyModel
import json
import time
import logging

logger = logging.getLogger('Main')
class LangHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        # print(self.reverse_url)
        from models.public.confrom_model import LangForm
        F = LangForm(self.request.arguments)
        if F.validate():
            if F.lang.data == "cn":
                self.set_secure_cookie("lang_str", "en", expires_days=99999)
            else:
                self.set_secure_cookie("lang_str", "cn", expires_days=99999)
        echo_dist = {}
        echo_dist['reponse_status'] = 5
        from models.public.headers_model import DateEncoder
        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        self.finish()