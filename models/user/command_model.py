# coding = utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import hashlib
import datetime
import config
from handlers.myredis.redis_class import RedisClass
import json
import time

logger = logging.getLogger('Main')
class CommcandModel():
    # 命令
    @gen.coroutine
    def setMarginCommcand(self, uaid, followid, type):
        from handlers.myredis.redis_class import RedisClass
        CommcandDist = {}
        CommcandDist["fx_type"] = type
        CommcandDist["sendid"] = int(uaid)
        CommcandDist["followid"] = int(followid)
        R = RedisClass()
        yield R.add_TotalConsole(CommcandDist)
        return

    @gen.coroutine
    def setNewMarginCommcand(self, uaid, followid, type):
        from handlers.myredis.redis_class import RedisClass
        CommcandDist = {}
        CommcandDist["fx_type"] = type
        CommcandDist["sendid"] = int(uaid)
        CommcandDist["followid"] = int(followid)
        R = RedisClass()
        yield R.add_Console_list(CommcandDist)
        return