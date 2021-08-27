#coding=utf-8
# from handlers.main.main_handler import IndexHandler
from handlers.user.user_urls import user_urls
# from handlers.huac.huac_urls import huac_urls
from handlers.user_admin.admin_urls import user_admin_urls
from handlers.admin.admin_urls import admin_urls
from handlers.public.public_urls import public_urls
from handlers.user_admin.admin_handler import AdminHandler

handlers = [
    # (r'/', IndexHandler),
    (r'/', AdminHandler),
]

handlers += user_urls
handlers += user_admin_urls
handlers += admin_urls
handlers += public_urls
# handlers += huac_urls