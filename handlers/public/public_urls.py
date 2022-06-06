#coding=utf-8
from handlers.public.error import ErrorHandler
# from handlers.public.qrcode import QrCode_Handler
from handlers.public.recaptcha import Recaptcha_Handler

public_urls = [
    (r'/error', ErrorHandler),
    # (r"/qrcode", QrCode_Handler),
    (r"/recaptcha", Recaptcha_Handler),
    (r'.*', ErrorHandler),
]