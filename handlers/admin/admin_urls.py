# coding = utf-8
#coding=utf-8
from handlers.admin.admin_handler import AdminHandler
from handlers.admin.posts_handler import PostsHandler
from handlers.admin.proxy_handler import ProxyHandler
from handlers.admin.proxy_info_handler import ProxyInfoHandler
from handlers.admin.pay_order_handler import PayOrderHandler
from handlers.admin.proxy_account_verify_handler import ProxyAccountVerifyHandler
from handlers.admin.img_handler import ImgHandler
from handlers.admin.strategy_handler import StrategyHandler
from handlers.admin.strategy_redis_handler import StrategyRedisHandler

admin_urls = [
    (r'/adminSZba2qjbydxVhMJpuKfy/', AdminHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/index', AdminHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/posts', PostsHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/pay_order', PayOrderHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/img', ImgHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/proxy', ProxyHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/proxy_info', ProxyInfoHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/proxy_account_verify', ProxyAccountVerifyHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/strategy', StrategyHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/strategy_redis', StrategyRedisHandler),
]