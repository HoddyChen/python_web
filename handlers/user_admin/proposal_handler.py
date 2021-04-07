#coding=utf-8
import tornado
import config
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
from models.public.confrom_model import ProposalForm
from models.user.cs_model import CsModel
import json
import logging

logger = logging.getLogger('Main')
class ProposalHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        page_main = {}
        page_main['lang'] = self.get_lang()
        page_main['title_website'] = config.WEBSITE_NAME
        if self.session['web_uid'] == None:
            # 退出
            # yield self.render("user/login.html", page_main=page_main)
            yield self.redirect("/user/index")
            return
        else:
            F = ProposalForm(self.request.arguments)
            if F.validate():
                cookie_dist = self.getCookie()
                page_main.update(cookie_dist)
                if F.fx_type.data == "add_proposal":
                    page_main['title_type'] = self.locale.translate("提交新提案")
                    yield self.render('user/index_add_proposal.html', page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proposal":
                    page_main['title_type'] = self.locale.translate("提案列表")
                    yield self.render('user/index_proposal_list.html', page_main=page_main, session=self.session)
                    return
                elif F.fx_type.data == "list_proposal_info":
                    page_main['title_type'] = self.locale.translate("提案内容")
                    page_main['fx_id'] = F.fx_id.data
                    yield self.render('user/index_proposal_info_list.html', page_main=page_main, session=self.session)
                    return
                else:
                    page_main['title_type'] = self.locale.translate("帮助与常见问题")
                    page_main['th_num'] = 2
                    yield self.render('user/index_help_list.html', page_main=page_main, session=self.session)
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
        if self.session['web_uid'] == None:
            # 退出
            echo_dist['reponse_status'] = -1
        else:
            # print("SS:", self.request.arguments)
            F = ProposalForm(self.request.arguments)
            if F.validate():#and F.cla.data == "SendError"
                echo_dist['reponse_status'] = 5
                C = CsModel()
                if F.fx_type.data == "add_proposal":
                    # 修改策略名称
                    m_dist = yield C.set_Cs(self.session['web_uid'], F.fx_id.data, F.fx_name.data, F.fx_text.data)
                    if m_dist != None:
                        if m_dist == -1:
                            echo_dist['reponse_status'] = -1
                            echo_dist['echo'] = self.locale.translate("保存失败！")
                        else:
                            if F.fx_id.data > 0:
                                echo_dist['data'] = yield C.getCs_info_List(self.session['web_uid'], F.fx_id.data,
                                                                            F.start.data, F.length.data)
                                echo_dist['id'] = self.session['web_uid']
                                echo_dist['server_text'] = self.locale.translate("客服")
                    else:
                        echo_dist['reponse_status'] = -2
                        echo_dist['echo'] = self.locale.translate("发生意外错误！")
                elif F.fx_type.data == "list_proposal":
                    echo_dist['data'] = yield C.getCsList(self.session['web_uid'], F.start.data, F.length.data)
                elif F.fx_type.data == "list_proposal_info":

                    echo_dist['data'] = yield C.getCs_info_List(self.session['web_uid'], F.fx_id.data, F.start.data, F.length.data)
                    echo_dist['id'] = self.session['web_uid']
                    echo_dist['server_text'] = self.locale.translate("客服")
                elif F.fx_type.data == "get_text":
                    echo_dist['data'] = yield C.getPostContent(F.fx_id.data)
                else:
                    page_papa = {}
                    page_papa['start'] = self.get_argument('start', 0)
                    page_papa['length'] = self.get_argument('length', 0)
                    page_papa['search'] = self.get_argument('search[value]', "0")
                    page_papa['prc_type'] = 5
                    # page_papa['page_num'] = self.get_argument('page_num', 10)
                    echo_dist["prc_type"] = page_papa['prc_type']
                    echo_dist['data'] = yield C.getPostsList(page_papa)
                # print(echo_dist['data'])
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