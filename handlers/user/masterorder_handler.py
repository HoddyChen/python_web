#coding=utf-8
#订单视图
import tornado
# from handlers.base.base_handler import BaseHandler
from datetime import datetime
from models.user.user_model import UserModel

class MasterOrderHandler(tornado.web.RequestHandler):
    def get(self):
        pass
        # self.render("user/login.html", next=self.get_argument("next"))

    #登录成功附加别的属性
    def success_login(self, user):
        user.last_login = datetime.now()
        user.loginnum += 1
        self.db.add(user)
        self.db.commit()
        self.session.set('username', user.user_name)