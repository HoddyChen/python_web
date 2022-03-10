

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
class StrategyRedisHandler(SessionHandler, BaseHandler):
    @gen.coroutine
    def post(self):
        echo_dist = {}
        page_main = {}
        if self.session['ManagerUid'] == None:
            # yield self.render("admin/login.html", page_main=page_main)
            yield self.redirect("adminSZba2qjbydxVhMJpuKfy/")
            # yield self.redirect("/adminSZba2qjbydxVhMJpuKfy/", permanent=False)
            return
        else:
            page_main['strategy_id'] = self.get_argument('strategy_id', 0)
            page_main['fx_type'] = self.get_argument('fx_type', None)
            R = RedisClass()
            echo_dist['reponse_status'] = 5
            if page_main['fx_type'] == "set_line":
                # 设置在线时间
                R.RH.set('own_strategy' + str(page_main['strategy_id']), int(time.time()))
            elif page_main['fx_type'] == "get_line":
                time_line = R.RH.get('own_strategy' + str(page_main['strategy_id']))
                if (int(time.time()) - int(time_line)) < 1000:
                    echo_dist['echo'] = 1
                else:
                    echo_dist['echo'] = 0
            else:
                echo_dist['echo'] = self.locale.translate("无此命令")
                echo_dist['reponse_status'] = 1
        logger.debug(echo_dist)
        from models.public.headers_model import DateEncoder
        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        # self.write(json.dumps(echo_dist))
        self.finish()