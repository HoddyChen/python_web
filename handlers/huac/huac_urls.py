#coding=utf-8
from handlers.huac.index_handler import IndexHandler
from handlers.huac.weixi_handler import WeixiHandler

huac_urls = [
    (r"/hauc/weixi", WeixiHandler),
    (r"/hauc/index", IndexHandler),
]