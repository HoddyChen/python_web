#coding=utf-8
import tornado
import re
import json
import time
import logging
import hashlib
import os
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import StrategyForm
from models.public.confrom_model import InfoForm
from handlers.myredis.redis_class import RedisClass
from models.user.user_model import UserModel
from models.user.strategy_model import StrategyModel
from models.user.order_model import OrderModel
from models.public.confrom_model import get_ErrorForm

logger = logging.getLogger('Main')
class InfoHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME
        if self.session['web_uid'] == None:
            # 退出
            # yield self.render("user/login.html", page_main=page_main)
            yield self.redirect("/index")
            return
        else:
            F = StrategyForm(self.request.arguments)
            if F.validate():
                cookie_dist = self.getCookie()
                page_main.update(cookie_dist)
                if F.fx_type.data == "edit_info":
                    S = StrategyModel()
                    s_data = yield S.getStrategyInfo(self.session['web_uid'], cookie_dist["current_strategy"], None)
                    page_main.update(s_data)
                    yield self.render('user/index_edit_info.html', page_main=page_main, session=self.session)
                    return
                if F.fx_type.data == "edit_info_comment":
                    O = OrderModel()
                    page_main['order_num'] = yield O.get_PositionOrderNum(cookie_dist["current_strategy"])
                    S = StrategyModel()
                    s_data = yield S.getStrategyInfo(self.session['web_uid'], cookie_dist["current_strategy"], None)
                    # print(s_data)
                    page_main.update(s_data)
                    yield self.render('user/index_edit_info_comment.html', page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "edit_logo":
                    S = StrategyModel()
                    s_data = yield S.getStrategyInfo(self.session['web_uid'], cookie_dist["current_strategy"], None)
                    page_main.update(s_data)
                    page_main['logo_url'] = "" if page_main['logo_url'] is None else page_main['logo_url']
                    yield self.render('user/index_file_upload.html', page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "edit_url_pass":
                    S = StrategyModel()
                    s_data = yield S.getProxyUrl(F.fx_id.data)
                    if s_data != None:
                        page_main.update(s_data)
                    s_data2 = yield S.getAccount(F.fx_id.data)
                    if s_data2 != None:
                        page_main.update(s_data2)
                    page_main['fx_id'] = F.fx_id.data
                    print(page_main)
                    yield self.render('user/index_edit_url_pass.html', page_main=page_main, session=self.session)
                    return
                else:
                    yield self.redirect("/user/index")
                    return
            else:
                # 表单错误
                logger.error(get_ErrorForm(F))
                self.render('user/500.html')
                return
        self.finish()

    @gen.coroutine
    def post(self):
        echo_dist = {}
        F = InfoForm(self.request.arguments)
        if self.session['web_uid'] == None:
            # 退出
            echo_dist['reponse_status'] = -1
        else:
            # print("SS:", self.request.arguments)

            cookie_dist = self.getCookie(1)
            if F.validate():#and F.cla.data == "SendError"
                echo_dist['reponse_status'] = 5

                S = StrategyModel()
                if F.fx_type.data == "edit_info":
                    # 修改策略名称
                    par4 = ".*?浩.*"
                    vol4 = re.compile(par4).findall(F.fx_name.data)
                    par5 = ".*?fxcns.*"
                    vol5 = re.compile(par5).findall(F.fx_name.data)
                    par6 = ".*?6copy.*"
                    vol6 = re.compile(par6).findall(F.fx_name.data)

                    if len(vol4) > 0 or len(vol5) > 0 or len(vol6) > 0:
                        echo_dist['reponse_status'] = -3
                        echo_dist['echo'] = self.locale.translate("策略名称中不能包括'浩'或6copy,fxcns！")
                    else:
                        m_dist = yield S.edit_info(self.session['web_uid'], self.get_user_ip(), F.fx_name.data, None,
                                                   cookie_dist["current_strategy"])
                        if m_dist != None:
                            if m_dist == -1:
                                echo_dist['reponse_status'] = -1
                                echo_dist['echo'] = self.locale.translate("保存失败！")
                            else:
                                self.set_secure_cookie("current_ma_name" + str(self.session['web_uid']),
                                                       "null" if F.fx_name.data == None else F.fx_name.data)
                        else:
                            echo_dist['reponse_status'] = -2
                            echo_dist['echo'] = self.locale.translate("发生意外错误！")
                elif F.fx_type.data == "edit_info_comment":
                    # 修改策略订单备注
                    par4 = ".*?fxcns.*"
                    vol4 = re.compile(par4).findall(F.comment.data)
                    par5 = ".*?6copy.*"
                    vol5 = re.compile(par5).findall(F.comment.data)
                    if len(vol4) > 0 or len(vol5) > 0:
                        echo_dist['reponse_status'] = -3
                        echo_dist['echo'] = self.locale.translate("策略名称中不能包括'fxcns'或'6copy'！")
                    else:
                        m_dist = yield S.edit_info_comment(self.session['web_uid'], self.get_user_ip(), F.comment.data, cookie_dist['current_key_ma'],
                                                           cookie_dist["current_strategy"])
                        if m_dist != None:
                            if m_dist == -1:
                                echo_dist['reponse_status'] = -1
                                echo_dist['echo'] = self.locale.translate("保存失败！")
                        else:
                            echo_dist['reponse_status'] = -2
                            echo_dist['echo'] = self.locale.translate("发生意外错误！")
                elif F.fx_type.data == "edit_url_pass":
                    # 修改URL
                    md5_str = str(F.urlpass.data) + str(F.fx_id.data)
                    # print(md5_str)
                    urlkey = hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()[8:-8]
                    m_dist = yield S.edit_url_key(self.get_user_ip(), F.pu_status.data, F.urlpass.data, F.fx_id.data, urlkey)
                    if type(m_dist) == type({}):
                        if m_dist.get('@out_mflag') < 0:
                            echo_dist['reponse_status'] = -1
                            echo_dist['echo'] = self.locale.translate("保存失败！")
                        else:
                            echo_dist['urlkey'] = "https://www.6copy.com/h?k=" + m_dist['@out_url_key']
                            echo_dist['pu_status'] = m_dist['@out_mflag']
                            echo_dist['reponse_status'] = 5
                    else:
                        echo_dist['reponse_status'] = m_dist
                        echo_dist['echo'] = self.locale.translate("发生意外错误！")
                elif F.fx_type.data == "edit_logo":
                    file_h = self.request.files['file']
                    key_text = cookie_dist["current_strategy"] + str(self.session['web_uid'])
                    file_name = hashlib.md5(key_text.encode(encoding='UTF-8')).hexdigest()
                    filePath = os.path.join(os.getcwd(), "static", "faceimg")
                    # print(os.getcwd())
                    # print(filePath)
                    for file in file_h:
                        # print(file)
                        # print(file.content_type)
                        # file['body']
                        extension_name = os.path.splitext(file['filename'])[1]
                        img_type = ".jpg .gif .png"
                        if img_type.find(extension_name) >= 0:
                            filePath = os.path.join(filePath, file_name + extension_name)
                            with open(filePath, 'wb') as f:
                                f.write(file['body'])
                        else:
                            echo_dist['reponse_status'] = -1
                            echo_dist['echo'] = self.locale.translate("上传的文件类型，仅限") + img_type
                        break
                    if echo_dist['reponse_status'] == 5:
                        # 写入头像数据库
                        m_dist = yield S.edit_info(self.session['web_uid'], self.get_user_ip(), None, file_name + extension_name,
                                                   cookie_dist["current_strategy"])
                        if m_dist != None:
                            if m_dist == -1:
                                echo_dist['reponse_status'] = -1
                                echo_dist['echo'] = self.locale.translate("数据库保存失败！")
                                echo_str = "false"
                            else:
                                self.set_secure_cookie("current_logo_url", file_name + extension_name)
                                echo_str = "true"
                                echo_dist['echo'] = self.locale.translate("其他错误！")
                        else:
                            echo_str = "false"
                            echo_dist['echo'] = self.locale.translate("数据库保存失败！")
                    else:
                        echo_str = "false"
                        echo_dist['echo'] = self.locale.translate("上传的文件类型")
                else:
                    echo_dist['echo'] = self.locale.translate("其他错误4")
                    echo_dist['reponse_status'] = 1
            else:
                # 表单错误
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
        # from models.public.headers_model import DateEncoder
        # yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        if F.fx_type.data == "edit_logo":
            self.write(echo_str)
        else:
            self.write(json.dumps(echo_dist))
        self.finish()