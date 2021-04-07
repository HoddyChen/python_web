# coding = utf-8
#管理员/资讯修改与新增
import tornado
from tornado.ioloop import IOLoop
from tornado import gen
from handlers.base.base_handler import BaseHandler
from handlers.session.session_handler import SessionHandler
import config
from models.public.confrom_model import AdminPostEditForm
from models.admin.posts_model import PostsModel
from models.public.headers_model import DateEncoder
import json
import datetime

class PostsHandler(SessionHandler, BaseHandler):

    @gen.coroutine
    def get(self):
        # 新增或修改
        # print("p:", self.get_lang())
        page_main = {}
        page_echo = {}
        page_main['title_website'] = config.WEBSITE_NAME + "管理区"
        if self.session['ManagerUid'] == None:
            yield self.render("admin/login.html", page_main=page_main)
            # yield self.redirect("/adminSZba2qjbydxVhMJpuKfy/", permanent=False)
            return
        page_main['lang'] = self.get_argument('lang', "")
        prc_type = self.get_argument('prc_type', None)
        fx_type = self.get_argument('fx_type', None)
        page_echo['pt_name_cn'] = ""
        page_echo['pt_name_en'] = ""
        page_echo['post_content'] = ""
        page_echo['post_title'] = ""
        page_echo['post_excerpt'] = ""
        page_main['fx_type'] = fx_type
        page_main['title_main'] = "管理区"
        page_main['title_type'] = "资讯"
        page_main['id'] = self.get_argument('id', 0)
        P = PostsModel()
        type_dist = yield P.getPostsTypeList()
        # print(type_dist)
        if fx_type == "list_posts":
            page_main['news_status'] = 1
            yield self.render("admin/index_posts_list.html", page_main=page_main, type_dist=type_dist, session=self.session, prc_type=prc_type)
            return
        elif fx_type == "recycle":
            #回收站
            page_main['news_status'] = 0
            # page_list, allnum = yield AdminNews_Models.listNews(page_main)
            # print(page_list)
            yield self.render("admin_con/index_news_list.html", page_main=page_main,
                              type_dist=type_dist, session=self.session, prc_type=prc_type)
            return
        elif fx_type == None:
            # 转错误页
            self.redirect('/error', permanent=False)
            return
        elif fx_type == "add_post":
            page_main['title_full'] = "新增"

        elif fx_type == "edit_post" and page_main['id'] != 0:
            page_main['title_full'] = "编辑"
            page_echo = yield P.getPostContent(page_main['id'])
            # print(page_echo)
        yield self.render("admin/index_posts_edit.html", page_main=page_main, type_dist=type_dist, session=self.session, page_echo=page_echo)
        return

    @gen.coroutine
    def post(self):
        fx_type = self.get_argument('fx_type', None)
        echo_dist = {}
        echo_dist['data'] = []
        echo_dist["recordsTotal"] = 0
        echo_dist["recordsFiltered"] = 0
        echo_dist['echo_title'] = "编辑资讯"
        if self.session['ManagerUid'] == None:
            echo_dist['echo_title'] = "登陆"
            echo_dist['echo'] = "登陆失效"
            echo_dist['ok_status'] = 0
        else:
            P = PostsModel()
            if fx_type == "list_posts" or fx_type =="recycle":
                # 默认列表
                # 列表用
                page_papa = {}
                page_papa['start'] = self.get_argument('start', 0)
                page_papa['length'] = self.get_argument('length', 0)
                page_papa['search'] = self.get_argument('search[value]', "0")
                page_papa['prc_type'] = self.get_argument('prc_type', 0)
                # page_papa['page_num'] = self.get_argument('page_num', 10)
                echo_dist["prc_type"] = page_papa['prc_type']
                echo_dist['data'] = yield P.getPostsList(page_papa)
                # print(page_list[-1])
                if len(echo_dist.get('data')) > 0:
                    if 'allnum' in echo_dist['data'][-1]:
                        allnum = echo_dist['data'].pop()
                        echo_dist["recordsTotal"] = allnum['allnum']
                        echo_dist["recordsFiltered"] = allnum['allnum']

            elif fx_type == "edit_post" or fx_type =="add_post":
                F = AdminPostEditForm(self.request.arguments)
                if F.validate():
                    # if F.comment_flag.data == "on":
                    #     comment_flag = 1
                    # else:
                    #     comment_flag = 0
                    form_dist = {
                        "uid": self.session['ManagerUid'],
                        "post_id": F.id.data,
                        "post_title": F.post_title.data,
                        "posts_type_id": F.posts_type_id.data,
                        "post_status": F.post_status.data,
                        # "comment_flag": F.comment_flag.data,
                        "post_excerpt": F.post_excerpt.data,
                        "tags_str": F.tags.data,
                        "post_content": F.post_content.data,
                    }
                    if int(form_dist['post_id']) != 0:
                        # 修改
                        flag = yield P.editPost(form_dist)
                        if flag == True:
                            # 字符转列表
                            tags_dist = yield P.formatToList(form_dist['tags_str'])
                            # 检查缺少的标签并增加
                            yield P.chickNewTags(tags_dist)
                            # 检查文章与标签的关联，得到缺少的标签关联, IDTuple
                            tags_Tuple_List, tags_dell_list = yield P.getPostTagsTuple(int(form_dist['post_id']), tags_dist)
                            # print("tags_Tuple_list:%s" % tags_Tuple_List)
                            # 增加文章与标签的关联
                            yield P.addPostsTags(tags_Tuple_List)
                            # 删除多余的文章与标签的关联
                            yield P.delOldTags(tags_dell_list)
                            yield P.chickPostType(form_dist['post_id'], form_dist['posts_type_id'])
                            # yield Mysql_log_Models.addMysqlLog("admin-editNews",
                            #                                "news_id:" + str(form_dist['news_id']) + ",news_status:" + str(
                            #                                    form_dist['news_status']), self.session['uid'])

                            echo_dist['echo'] = "修改成功"
                            echo_dist['ok_status'] = 5
                        elif flag == False:
                            echo_dist['echo'] = "修改失败"
                            echo_dist['ok_status'] = 2
                        elif flag == None:
                            echo_dist['echo'] = "已经存在相同的文章"
                            echo_dist['ok_status'] = 3
                    else:
                        #新增
                        post_id = yield P.addPost(form_dist)
                        if post_id:
                            # 字符转列表
                            tags_list = yield P.formatToList(form_dist['tags_str'])
                            # 检查缺少的标签并增加
                            yield P.chickNewTags(tags_list)
                            # 获得所有标签, IDTuple
                            tags_Tuple_List = yield P.getAllTagsTuple(post_id, tags_list)
                            # print("tags_Tuple_list:%s" % tags_Tuple_List)
                            # 增加文章与标签的关联
                            yield P.addPostsTags(tags_Tuple_List)
                            yield P.chickPostType(post_id, form_dist['posts_type_id'])
                            # yield Mysql_log_Models.addMysqlLog("admin-addPosts", "post_id:" + str(form_dist['post_id']) + ",news_status:" + str(form_dist['news_status']), self.session['uid'])
                            echo_dist['echo'] = "新增成功"
                            echo_dist['ok_status'] = 5
                        elif post_id == False:
                            echo_dist['echo'] = "新增失败"
                            echo_dist['ok_status'] = 2
                        elif post_id == None:
                            echo_dist['echo'] = "已经存在相同的文章"
                            echo_dist['ok_status'] = 3
                else:
                    # 表单错误
                    from models.public.confrom_model import get_ErrorForm
                    echo_dist['echo'] = get_ErrorForm(F)
                    echo_dist['ok_status'] = 1
            elif fx_type == "del":
                #删除
                flag = yield P.delPost(self.get_argument('id', 0))
                if flag:
                    echo_dist['echo'] = "删除成功"
                    echo_dist['ok_status'] = 5
                else:
                    echo_dist['echo'] = "删除失败"
                    echo_dist['ok_status'] = 1
            else:
                echo_dist[''] = "你好，黑客！"

        # print("json:%s" % json.dumps(echo_dist))

        yield self.write(json.dumps(echo_dist, cls=DateEncoder))
        self.finish()


