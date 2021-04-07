# coding = utf-8
from libs.db.dbsession import pool
from libs.db.dbsession import fx_escape_string
from tornado import gen
import logging
import hashlib
import datetime
import config
from handlers.myredis.redis_class import RedisClass
import json

logger = logging.getLogger('Main')
class PostsModel():

    @gen.coroutine
    def getPostsTypeList(self):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT posts_type.posts_type_id,posts_type.posts_type_name_cn,posts_type.posts_type_name_en," \
                      "posts_type.posts_type_status,posts_type.vipid, posts_type.`level` FROM posts_type " \
                      "WHERE posts_type_status >= 5 ORDER BY posts_type.posts_type_id DESC"
                yield cursor.execute(sql)
                datas = cursor.fetchall()
        return datas

    # 得到博文的列表
    @gen.coroutine
    def getPostsList(self, page_main=None):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                # print("search:", page_main.get('search'))
                from_str = """FROM posts_type
                        INNER JOIN posts_type_relationship ON posts_type.posts_type_id = posts_type_relationship.posts_type_id
                        INNER JOIN posts ON posts_type_relationship.post_id = posts.post_id
                        INNER JOIN users ON posts.uid = users.uid"""
                sql = ""
                # from_str +
                if page_main.get('prc_type') != None and page_main.get('prc_type') != 0 and page_main.get('prc_type') != "None":
                    sql = " WHERE posts_type.posts_type_id = %s" % page_main.get('prc_type')

                if page_main != None and page_main.get('search') != "0" and page_main.get('search') != "":
                    search = "%" + page_main.get('search') + "%"
                    if sql == "":
                        sql = " WHERE posts.post_title like '%s'" % search
                    else:
                        sql = sql + " AND posts.post_title like '%s'" % search
                sql2 = "SELECT COUNT(*) as allnum " + from_str + sql
                # print(sql2)
                yield cursor.execute(sql2)
                allnum = cursor.fetchone()
                if allnum['allnum'] > 0:
                    start = 0 if page_main.get('start') == None else page_main.get('start')
                    length = 10 if page_main.get('length') == None else page_main.get('length')
                    sql3 = "SELECT posts_type.posts_type_name_cn,posts.post_id,posts.post_date,posts.post_status,posts.post_modified,users.uname,posts.post_title," \
                           "posts.post_id,posts_type.posts_type_id,posts.read_count " + from_str + sql + " ORDER BY posts.post_modified DESC limit %s, %s" % (int(start), int(length))
                    # print(sql3)
                    yield cursor.execute(sql3)
                    datas = cursor.fetchall()
                    if len(datas) > 0:
                        datas.append(allnum)
                        # print(datas)
                        return datas
                    else:
                        return []
                else:
                    return []

    # 得到博文内容
    @gen.coroutine
    def getPostContent(self, id):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT posts.post_id,posts.uid,posts.post_date,posts.post_content,posts.post_title,posts.post_excerpt," \
                      "posts.post_status,posts.post_password,posts.post_modified,posts_type.posts_type_name_cn," \
                      "posts_type.posts_type_name_en,posts_type.posts_type_status,posts_type.posts_type_id FROM posts " \
                      "INNER JOIN posts_type_relationship ON posts.post_id = posts_type_relationship.post_id " \
                      "INNER JOIN posts_type ON posts_type_relationship.posts_type_id = posts_type.posts_type_id " \
                      "WHERE posts.post_id = %s"
                yield cursor.execute(sql, (id,))
                datas = cursor.fetchone()

                if datas:
                    sql2 = "SELECT posts_terms.pt_name_cn,posts_terms.pt_name_en FROM posts_post_term INNER JOIN posts_terms ON posts_post_term.pt_id = posts_terms.pt_id WHERE posts_post_term.post_id = %s"
                    yield cursor.execute(sql2, (id,))
                    datas2 = cursor.fetchall()
                    tag_str_cn = ""
                    tag_str_en = ""
                    for tag in datas2:
                        tag_str_cn = tag_str_cn + tag['pt_name_cn'] + ","
                        if tag['pt_name_en'] != None and tag['pt_name_en'] != "":
                            tag_str_en = tag_str_en + tag['pt_name_en'] + ","
                    datas['pt_name_cn'] = tag_str_cn
                    datas['pt_name_en'] = tag_str_en
                return datas

    @gen.coroutine
    def addPost(self, Post_dist):
        # 新增博文
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql = "SELECT post_id FROM posts WHERE post_title = '%s'"
                    # logger.info(sql)
                    yield cursor.execute(sql % (Post_dist['post_title']))
                    datas = cursor.fetchone()
                    if datas == None:
                        up_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        sql2 = "INSERT INTO posts(uid,post_status,post_date,post_modified,post_title,post_excerpt,post_content)" \
                               " VALUES(%s, %s, %s, %s, %s, %s, %s)"
                        yield cursor.execute(sql2, (
                            Post_dist['uid'], Post_dist['post_status'], up_date, up_date, Post_dist['post_title'],
                            Post_dist['post_excerpt'], Post_dist['post_content']))
                        Post_id = conn.insert_id()
                        # Post_id = cursor.lastrowid
                        logger.debug("Post_id:%s" % Post_id)
                        if Post_id > 0:
                            yield conn.commit()
                            return Post_id
                        else:
                            yield conn.rollback()
                            logger.error("[PostsModel:addPost--error]")
                            return False
                    else:
                        return None
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[PostsModel:addPost] %s" % err)
                    return False

    @gen.coroutine
    def editPost(self, news_dist):
        # 修改博文
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    up_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql2 = "update posts set `post_title` = %s, `post_status`=%s, `post_excerpt`=%s,`post_content`=%s," \
                           "`post_modified`=%s WHERE post_id = %s"
                    # print(sql2 % (news_dist['post_title'], news_dist['post_status'], news_dist['post_excerpt'],
                    #                              news_dist['post_content'], up_date, int(news_dist['post_id'])))
                    yield cursor.execute(sql2, (news_dist['post_title'], news_dist['post_status'], news_dist['post_excerpt'],
                                                 news_dist['post_content'], up_date, int(news_dist['post_id'])))
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[PostsModel:editPost] %s" % err)
                    return False

    @gen.coroutine
    def addPostsTags(self, tags_Tuple_list):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql2 = "INSERT INTO posts_post_term(post_id,pt_id) VALUES(%s,%s)"
                    yield cursor.executemany(sql2, tags_Tuple_list)
                    yield conn.commit()
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[PostsModel:addPostsTags] %s" % err)
                    return False

    @gen.coroutine
    def formatToList(self, tags_str):
        # 转列表
        import re
        tags_list = re.compile("([\s\S]+?)[\.\,]").findall(tags_str + ",")
        # print("tags_list", tags_list)
        return tags_list

    @gen.coroutine
    def chickNewTags(self, tags_list):
        # 检查缺少的标签并增加
        current_tags = yield self.getTags(tags_list)
        current_tags_list = []
        for tags in current_tags:
            current_tags_list.append(tags['pt_name_cn'])
        logger.debug("current_tags_list:%s" % current_tags_list)
        addTupleList = []
        for tag in tags_list:
            if tag in current_tags_list:
                continue
            else:
                tupleList = (tag, "")
                addTupleList.append(tupleList)
        logger.debug("addTupleList:%s" % addTupleList)
        yield self.addTags(addTupleList)
        return

    @gen.coroutine
    def delPost(self, id):
        # 删除博文，标志为0
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql2 = "UPDATE posts SET post_status = 0 WHERE post_id = %s"
                    # print("sql2:%s" % id)
                    yield cursor.execute(sql2, id)
                    yield conn.commit()
                    # news_id = cursor.lastrowid
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[PostsModel,delPost] %s" % err)
                    return False

    @gen.coroutine
    def delOldTags(self, tags_dell_list):
        # 检查不需要的标签并删除
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql2 = "DELETE FROM posts_post_term WHERE pt_id = %s AND post_id = %s"
                    # print("sql2:%s" % sql2)
                    yield cursor.executemany(sql2, tags_dell_list)
                    yield conn.commit()
                    # news_id = cursor.lastrowid
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[PostsModel,delOldTags] %s" % err)
                    return False

    @gen.coroutine
    def getTags(self, tags_list):
        # 已经有的标签
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                if len(tags_list) == 1:
                    tags_list.append("fxcns")
                sql = "select pt_id,pt_name_cn from posts_terms where `pt_name_cn` in %s"
                # print(sql)
                yield cursor.execute(sql, (tuple(tags_list),))
                rows = cursor.fetchall()
                rows2 = []
                if "fxcns" in tags_list:
                    tags_list.remove("fxcns")
                    for pt in rows:
                        if pt['pt_name_cn'] != "fxcns":
                            rows2.append(pt)
                    return rows2
                else:
                    return rows

    @gen.coroutine
    def addTags(self, addTupleList):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    if len(addTupleList) > 0:
                        sql2 = "INSERT INTO posts_terms(`pt_name_cn`,`pt_name_en`) VALUES(%s,%s)"
                        # print("sql2:%s" % sql2)
                        yield cursor.executemany(sql2, addTupleList)
                        yield conn.commit()
                    # news_id = cursor.lastrowid
                    return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[PostsModel,addTags] %s" % err)
                    return False

    @gen.coroutine
    def getAllTagsTuple(self, post_id, tags_list):
        # 获得所有标签,IDTuple
        current_tags_ALL = yield self.getTags(tags_list)
        logger.debug("current_tags_ALL:%s" % current_tags_ALL)
        tags_id_list = []
        for newtag_id in current_tags_ALL:
            tags_id_tuple = (post_id, newtag_id['pt_id'])
            tags_id_list.append(tags_id_tuple)
        return tags_id_list

    @gen.coroutine
    def getPostTagsTuple(self, post_id, tags_list):
        # 获得所有需要增加的标签,IDTuple
        current_tags_ALL = yield self.getTags(tags_list)
        tags_old = yield self.getPostTags(post_id)
        tags_old_list = []
        tags_new_list = []
        tags_dell_list = []
        for tags_new in current_tags_ALL:
            tags_new_list.append(tags_new['pt_id'])
        logger.debug("current_tags_ALL:%s" % current_tags_ALL)
        for tags in tags_old:
            tags_old_list.append(tags['pt_id'])
            if tags['pt_id'] not in tags_new_list:
                tags_dell_list.append((tags['pt_id'], post_id))
        logger.debug("tags_dell_list:%s" % tags_dell_list)
        news_tags_id_list = []
        for newstag in current_tags_ALL:
            if newstag['pt_id'] in tags_old_list:
                continue
            else:
                tags_id_tuple = (post_id, newstag['pt_id'])
                news_tags_id_list.append(tags_id_tuple)
        return news_tags_id_list, tags_dell_list

    @gen.coroutine
    def getPostTags(self, post_id):
        # 已经有的标签
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "select pt_id from posts_post_term where post_id = %s"
                yield cursor.execute(sql, (int(post_id),))
                rows = cursor.fetchall()
                return rows

    @gen.coroutine
    def chickPostType(self, post_id, posts_type_id):
        # 已经有的标签
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql = "SELECT post_id,posts_type_id FROM posts_type_relationship WHERE post_id = %s"
                yield cursor.execute(sql, (int(post_id),))
                rows = cursor.fetchone()
                try:
                    if rows:
                        if rows['posts_type_id'] == posts_type_id:
                            return True
                        else:
                            #修改
                            sql2 = "UPDATE posts_type_relationship SET `posts_type_id` = %s WHERE `post_id` = %s"
                            yield cursor.execute(sql2, (int(posts_type_id), int(post_id)))
                            yield conn.commit()
                            return True
                    else:
                        #新增
                        sql3 = "INSERT INTO posts_type_relationship(`post_id`,`posts_type_id`) VALUES(%s,%s)"
                        yield cursor.execute(sql3, (int(post_id), int(posts_type_id)))
                        yield conn.commit()
                        # news_id = cursor.lastrowid
                        return True
                except Exception as err:
                    yield conn.rollback()
                    logger.error("[PostsModel,chickPostType] %s" % err)
                    return False