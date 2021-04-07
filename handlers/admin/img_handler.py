#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import ImgForm
from models.public.confrom_model import InfoForm
from handlers.myredis.redis_class import RedisClass
from models.user.user_model import UserModel
from models.user.strategy_model import StrategyModel
import json
import time
import logging

logger = logging.getLogger('Main')
class ImgHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME + "管理区"
        if self.session['ManagerUid'] == None:
            # 退出
            # yield self.render("user/login.html", page_main=page_main)
            yield self.render("admin/login.html", page_main=page_main)
            return
        else:
            F = ImgForm(self.request.arguments)
            if F.validate():
                cookie_dist = self.getCookie(1)
                # page_main.update(cookie_dist)
                if F.fx_type.data == "add_img":
                    import hashlib
                    key_text = str(time.time())
                    page_main['file_name'] = hashlib.md5(key_text.encode(encoding='UTF-8')).hexdigest()
                    yield self.render('admin/index_img_upload.html', page_main=page_main, session=self.session)
                    return
                else:
                    yield self.redirect("/admin/index")
                    return
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                logger.error(get_ErrorForm(F))
                self.render('admin/500.html')
                return
        self.finish()

    @gen.coroutine
    def post(self):
        echo_dist = {}
        if self.session['ManagerUid'] == None:
            # 退出
            echo_dist['reponse_status'] = -1
        else:
            # print("SS:", self.request.arguments)
            F = ImgForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                echo_dist['reponse_status'] = 5
                echo_str = "false"
                if F.fx_type.data == "add_img":
                    file_h = self.request.files['file']
                    import os

                    filePath = os.path.join(os.getcwd(), "static", "bolgimg")
                    # print(os.getcwd())
                    # print(F.file_name.data)
                    for file in file_h:
                        # print(file)
                        # print(file.content_type)
                        # file['body']
                        extension_name = os.path.splitext(file['filename'])[1]
                        extension_name = extension_name.lower()
                        img_type = ".jpg .gif .png .PNG .GIF .JPG"
                        if img_type.find(extension_name) >= 0:
                            filePath = os.path.join(filePath, F.file_name.data + extension_name)
                            # print(filePath)
                            with open(filePath, 'wb') as f:
                                f.write(file['body'])
                        else:
                            echo_dist['reponse_status'] = -1
                            echo_dist['echo'] = self.locale.translate("上传的文件类型，仅限") + img_type
                        break
                    if echo_dist['reponse_status'] == 5:
                        # 写入头像数据库
                        # F.backurl.data + extension_name
                        echo_str = "ture"
                    else:
                        echo_str = "false"
                        echo_dist['echo'] = self.locale.translate("上传的文件类型")
                else:
                    echo_dist['echo'] = self.locale.translate("其他错误4")
                    echo_dist['reponse_status'] = 1
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
        # from models.public.headers_model import DateEncoder
        # yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        if F.fx_type.data == "add_img":
            self.write(echo_str)
        else:
            self.write(json.dumps(echo_dist))
        self.finish()