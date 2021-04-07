#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import ProxyInfoForm
from models.public.headers_model import Headers_Models
from models.user.proxy_order_model import ProxyOrderModel
import json
import logging

logger = logging.getLogger('Main')
class ProxyInfoHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME
        if self.session['ManagerUid'] == None:
            # 退出
            # yield self.render("user/login.html", page_main=page_main)
            yield self.render("admin/login.html", page_main=page_main)
            return
        else:
            F = ProxyInfoForm(self.request.arguments)
            if F.validate():
                # cookie_dist = self.getCookie()
                # page_main.update(cookie_dist)
                page_main['prc_type'] = F.fx_type.data
                P = ProxyOrderModel()
                if F.fx_type.data == "edit_proxy":
                    # 修改代理资料
                    data = yield P.CheckProxyInfo(self.session['web_uid'])
                    if len(data) > 0:
                        page_main['uname'] = data[0]['uname']
                        page_main['iban'] = data[0]['iban']
                        page_main['flag'] = data[0]['flag']
                        page_main['title_type'] = self.locale.translate("修改返佣资料")
                    else:
                        yield P.add_proxy_info(self.session['web_uid'])
                        page_main['uname'] = ""
                        page_main['iban'] = ""
                        page_main['flag'] = 0
                        page_main['title_type'] = self.locale.translate("新增返佣资料")
                    yield self.render("user/index_edit_proxy_info.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proxy":
                    # 代理列表
                    page_main['title_type'] = self.locale.translate("返佣管理")
                    data = yield P.getProxyGradePrice()
                    page_main['price_html'] = yield self.format_html(data)
                    page_main['th_num'] = 5
                    yield self.render("admin/index_proxy_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proxy_account":
                    # 各代理的列表
                    page_main['title_type'] = self.locale.translate("账户管理")
                    page_main['th_num'] = 4
                    yield self.render("user/index_proxy_account_list.html", page_main=page_main, session=self.session)
                    return
                else:
                    page_main['title_type'] = self.locale.translate("瑞讯银行瑞士账户申请")
                    # page_main['th_num'] = 2
                    yield self.render('admin/index_swissquote_open.html', page_main=page_main, session=self.session)
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
        echo_dist['data'] = []
        echo_dist["recordsTotal"] = 0
        echo_dist["recordsFiltered"] = 0
        if self.session['ManagerUid'] == None:
            # 退出
            echo_dist['reponse_status'] = -1
        else:
            # print("SS:", self.request.arguments)
            F = ProxyInfoForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                echo_dist['reponse_status'] = 5
                P = ProxyOrderModel()
                cookie_dist = self.getCookie(1)
                if F.fx_type.data == "edit_proxy":
                    # 修改
                    data = yield P.CheckProxyInfo(self.session['web_uid'])
                    if len(data) > 0:
                        if data[0]['flag'] == 0:
                            m_dist = yield P.set_proxy_info(self.session['web_uid'], F.uname.data, F.iban.data)
                    if m_dist == True:
                        echo_dist['reponse_status'] = 5
                        echo_dist['echo'] = self.locale.translate("保存成功！")
                    else:
                        echo_dist['reponse_status'] = -1
                        echo_dist['echo'] = self.locale.translate("保存失败！")
                elif F.fx_type.data == "edit_u_flag":
                    # 修改，修改状态
                    Ok_flag = yield P.set_proxy_u_flag(F.uid.data)
                    if Ok_flag == True:
                        echo_dist['reponse_status'] = 5
                        echo_dist['echo'] = self.locale.translate("修改成功")
                    else:
                        echo_dist['reponse_status'] = -2
                        echo_dist['echo'] = self.locale.translate("修改出错")
                elif F.fx_type.data == "edit_grade_price":
                    # 修改佣金
                    Ok_flag = yield P.set_proxy_grade_price(F.uid.data, F.grade_id.data)
                    if Ok_flag == True:
                        echo_dist['reponse_status'] = 5
                        echo_dist['echo'] = self.locale.translate("修改成功")
                    else:
                        echo_dist['reponse_status'] = -1
                        echo_dist['echo'] = self.locale.translate("修改失败")
                elif F.fx_type.data == "list_proxy":
                    page_papa = {}
                    page_papa['start'] = F.start.data
                    page_papa['length'] = F.length.data
                    page_papa['search'] = self.get_argument('search[value]', '0')
                    echo_dist['data'] = yield P.getProxyList(page_papa)
                elif F.fx_type.data == "list_proxy_account":
                    page_papa = {}
                    page_papa['start'] = F.start.data
                    page_papa['length'] = F.length.data
                    page_papa['search'] = self.get_argument('search[value]', '0')
                    echo_dist['data'] = yield P.getProxyAccountList(self.session['web_uid'], page_papa)
                else:
                    echo_dist['echo'] = self.locale.translate("无数据")
                    echo_dist['reponse_status'] = 5
                # print(echo_dist['data'])
                if F.fx_type.data == "list_proxy":
                    if len(echo_dist.get('data')) > 0:
                        if 'allnum' in echo_dist['data'][-1]:
                            allnum = echo_dist['data'].pop()
                            # print('allnum', allnum)
                            echo_dist["recordsTotal"] = allnum['allnum']
                            echo_dist["recordsFiltered"] = allnum['allnum']
                            # s_data.pop()
                    else:
                        echo_dist['echo'] = self.locale.translate("无数据")
                        echo_dist['reponse_status'] = 5
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                echo_dist['echo'] = get_ErrorForm(F)
                echo_dist['reponse_status'] = 1
        # print(echo_dist)
        from models.public.headers_model import DateEncoder
        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        # self.write(json.dumps(echo_dist))
        self.finish()

    @gen.coroutine
    def format_html(self, type_dist):
        price_html = '<select class="form-control show-tick" name="grade_id">'
        price_html = price_html + '<option value="" selected>-- 选择佣金 --</option>'
        for post_type in type_dist:
            price_html = price_html + '<option value="' + str(post_type['grade_id']) + '">' + str(post_type['grade_price']) + '</option>'
        price_html = price_html + ' </select>'
        from xml.sax.saxutils import escape
        return price_html