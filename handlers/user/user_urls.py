#coding=utf-8
from handlers.user.user_handler import UserHandler
from handlers.user.account_handler import AccountHandler
from handlers.user.order_handler import OrderHandler
from handlers.user.proxy_order_handler import ProxyOrderHandler
from handlers.user.copyorder_handler import CopyOrderHandler
from handlers.user.vcmail_handler import VcmailHandler
from handlers.user.sendmail_handler import SendmailHandler
from handlers.user.senderror_handler import SendOrderErrorHandler
from handlers.user.seperate_handler import SeperateHandler
from handlers.user.master_handler import MasterHandler
# from handlers.user.test_handler import TestHandler

user_urls = [
    (r"/user", UserHandler),
    (r"/account", AccountHandler),
    (r"/order", OrderHandler),
    (r"/proxyorder", ProxyOrderHandler),
    (r"/copyorder", CopyOrderHandler),
    (r"/sendmail", SendmailHandler),
    (r"/senderror", SendOrderErrorHandler),
    (r"/vcmail", VcmailHandler),
    (r"/master", MasterHandler),
    (r"/seperate", SeperateHandler),
    # (r"/test", TestHandler),
]