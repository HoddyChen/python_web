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
class SwissquoteProxyInfoHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME
        if self.session['swissquote_uid'] == None:
            # 退出
            # yield self.render("user/login.html", page_main=page_main)
            yield self.redirect("/swissquote")
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
                    data = yield P.CheckProxyInfo(self.session['swissquote_uid'])
                    if len(data) > 0:
                        page_main['uname'] = data[0]['uname']
                        page_main['iban'] = data[0]['iban']
                        page_main['flag'] = data[0]['flag']
                        page_main['title_type'] = self.locale.translate("修改返点资料")
                    else:
                        # yield P.add_proxy_info(self.session['swissquote_uid'])
                        page_main['uname'] = ""
                        page_main['iban'] = ""
                        page_main['flag'] = 0
                        page_main['title_type'] = self.locale.translate("新增返点资料")
                    yield self.render("user/swissquote_index_edit_proxy_info.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proxy_account":
                    # 列表
                    page_main['title_type'] = self.locale.translate("账户管理")
                    page_main['text1'] = self.locale.translate("通过本站开户专属链接开户成功、入金并开通MT4账户后, 可通过右边的")
                    page_main['text2'] = self.locale.translate("新增账户, 完成第一笔交易并平仓后, 可激活返点状态")
                    page_main['th_num'] = 4
                    yield self.render("user/swissquote_index_proxy_account_list.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "proxy_graup":
                    # 当前返点
                    page_main['title_type'] = self.locale.translate("返点简报")
                    # page_main['text1'] = self.locale.translate("通过本站开户专属链接开户成功、入金并开通MT4账户后, 可通过右边的")
                    # page_main['text2'] = self.locale.translate("新增账户, 完成第一笔交易并平仓后, 可激活返点状态")
                    page_main['group'] = yield P.getProxyGroup(self.session['swissquote_uid'])
                    if page_main['group'] == None:
                        yield P.add_proxy_info(self.session['swissquote_uid'])
                        page_main['group'] = yield P.getProxyGroup(self.session['swissquote_uid'])
                    # 统计总结算金额，单量all_proxy_profit - all_amount
                    page_main['all_proxy_profit'], page_main['all_profit'], page_main['all_amount'] = yield P.getProxySettlementAllCount(self.session['swissquote_uid'])
                    yield self.render("user/swissquote_index_proxy_group.html", page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proxy_accountclass":
                    # 用户分组列表
                    page_main['title_type'] = self.locale.translate("分组管理")
                    page_main['text1'] = self.locale.translate("设置分组后，返点历史数据可以根据分组计算结果")
                    page_main['th_num'] = 2
                    yield self.render("user/swissquote_index_proxy_accountclass_list.html", page_main=page_main, session=self.session)
                    return
                else:
                    page_main['title_type'] = self.locale.translate("瑞讯银行瑞士账户申请")
                    # page_main['th_num'] = 2
                    yield self.render('user/swissquote_index.html', page_main=page_main, session=self.session)
                    return
            else:
                # 表单错误
                from models.public.confrom_model import get_ErrorForm
                logger.error(get_ErrorForm(F))
                self.render('user/500.html')
                return
        self.finish()

    @gen.coroutine
    def post(self):
        echo_dist = {}
        echo_dist['data'] = []
        echo_dist["recordsTotal"] = 0
        echo_dist["recordsFiltered"] = 0
        if self.session['swissquote_uid'] == None:
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
                    data = yield P.CheckProxyInfo(self.session['swissquote_uid'])
                    if len(data) > 0:
                        if data[0]['flag'] == 0:
                            m_dist = yield P.set_proxy_info(self.session['swissquote_uid'], F.uname.data, F.iban.data)
                    else:
                        m_dist = yield P.add_proxy_info(self.session['swissquote_uid'], F.uname.data, F.iban.data)
                    if m_dist == True:
                        echo_dist['reponse_status'] = 5
                        echo_dist['echo'] = self.locale.translate("保存成功！")
                    else:
                        echo_dist['reponse_status'] = -1
                        echo_dist['echo'] = self.locale.translate("保存失败！")
                elif F.fx_type.data == "edit_proxy_accountclass":
                    # 修改分组名称
                    flag = yield P.CheckProxyAccountClassId(self.session['swissquote_uid'], F.gid.data)
                    if flag:
                        m_dist = yield P.set_proxy_account_class_name(self.session['swissquote_uid'], F.gid.data, F.user_class.data)
                        if m_dist == True:
                            echo_dist['reponse_status'] = 5
                            echo_dist['echo'] = self.locale.translate("保存成功！")
                        else:
                            echo_dist['reponse_status'] = -1
                            echo_dist['echo'] = self.locale.translate("保存失败！")
                    else:
                        echo_dist['reponse_status'] = -2
                        echo_dist['echo'] = self.locale.translate("分组不存在，保存失败！")
                elif F.fx_type.data == "edit_verify":
                    # 修改
                    Ok_flag = yield P.editPAVerify(self.session['swissquote_uid'], F.account.data, config.PROXY_PRICE)
                    if Ok_flag == 5:
                        echo_dist['reponse_status'] = 5
                        echo_dist['echo'] = self.locale.translate("返点激活成功")
                    elif Ok_flag == -1:
                        echo_dist['reponse_status'] = -1
                        echo_dist['echo'] = self.locale.translate("返点激活出错")
                    else:
                        echo_dist['reponse_status'] = -2
                        echo_dist['echo'] = self.locale.translate("返点激活失败！请在账户完成首笔交易并平仓后再试")
                elif F.fx_type.data == "add_proxy_account":
                    # 新增账户
                    Ok_flag = yield P.addProxyAccount(self.session['swissquote_uid'], F.account.data, F.a_code.data)
                    if Ok_flag == 5:
                        echo_dist['reponse_status'] = 5
                        echo_dist['echo'] = self.locale.translate("新增成功")
                    elif Ok_flag == -1:
                        echo_dist['reponse_status'] = -1
                        echo_dist['echo'] = self.locale.translate("新增失败")
                    elif Ok_flag == -2:
                        echo_dist['reponse_status'] = -2
                        echo_dist['echo'] = self.locale.translate("新增失败,账户已经绑定过")
                    else:
                        echo_dist['reponse_status'] = -3
                        echo_dist['echo'] = self.locale.translate("新增失败，账户验证失败，请检查填写信息的正确性")
                elif F.fx_type.data == "add_proxy_accountclass":
                    # 新增账户分组
                    Ok_flag = yield P.addProxyAccountClass(self.session['swissquote_uid'], F.user_class.data)
                    if Ok_flag == 5:
                        echo_dist['reponse_status'] = 5
                        echo_dist['echo'] = self.locale.translate("分组新增成功")
                    elif Ok_flag == -2:
                        echo_dist['reponse_status'] = -2
                        echo_dist['echo'] = self.locale.translate("新增失败,分组名称已经存在")
                    else:
                        echo_dist['reponse_status'] = -1
                        echo_dist['echo'] = self.locale.translate("分组新增失败")

                elif F.fx_type.data == "list_proxy_account":
                    page_papa = {}
                    page_papa['start'] = F.start.data
                    page_papa['length'] = F.length.data
                    page_papa['gid'] = F.gid.data
                    page_papa['search'] = self.get_argument('search[value]', '0')
                    echo_dist['data'] = yield P.getProxyAccountList(self.session['swissquote_uid'], page_papa)

                elif F.fx_type.data == "list_proxy_account_class":
                    # 读取分组列表
                    page_papa = {}
                    page_papa['start'] = F.start.data
                    page_papa['length'] = F.length.data
                    page_papa['search'] = self.get_argument('search[value]', '0')
                    echo_dist['data'] = yield P.getProxyAccountListClass(self.session['swissquote_uid'], page_papa)
                else:
                    echo_dist['echo'] = self.locale.translate("无数据")
                    echo_dist['reponse_status'] = 5
                # print(echo_dist['data'])
                if F.fx_type.data == "list_proxy_account" or F.fx_type.data == "list_proxy_account_class":
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
