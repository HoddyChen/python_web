# coding = utf-8
#coding=utf-8
from handlers.admin.admin_handler import AdminHandler
from handlers.admin.posts_handler import PostsHandler
from handlers.admin.proxy_handler import ProxyHandler
from handlers.admin.proxy_info_handler import ProxyInfoHandler
from handlers.admin.pay_order_handler import PayOrderHandler
from handlers.admin.proxy_account_verify_handler import ProxyAccountVerifyHandler
from handlers.admin.img_handler import ImgHandler

admin_urls = [
    (r'/adminSZba2qjbydxVhMJpuKfy/', AdminHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/index', AdminHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/posts', PostsHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/pay_order', PayOrderHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/img', ImgHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/proxy', ProxyHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/proxy_info', ProxyInfoHandler),
    (r'/adminSZba2qjbydxVhMJpuKfy/proxy_account_verify', ProxyAccountVerifyHandler),
]