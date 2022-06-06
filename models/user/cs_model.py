# coding = utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import hashlib
import datetime
import config
from handlers.myredis.redis_class import RedisClass
import json
import time

logger = logging.getLogger('Main')
class CsModel():
    # 得到客服的列表
    @gen.coroutine
    def getCsList(self, uid, start, length):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                sql0 = "SELECT count(*) as num FROM cs WHERE uid=%s and cs_status=1 and cs_type = 1"
                # print(sql0,uid)
                yield cursor.execute(sql0, uid)
                datas2 = cursor.fetchone()
                sql = "SELECT csid,cs_name,cs_text,reply_status,utime FROM cs WHERE uid=%s and cs_status=1 and cs_type = 1 ORDER BY cs_id DESC limit %s, %s"
                # print(sql% (uid, start, length))
                yield cursor.execute(sql, (uid, start, length))
                datas = cursor.fetchall()
                if len(datas) > 0:
                    datas.append({"allnum": datas2['num']})
                    return datas
                else:
                    return []

    @gen.coroutine
    def getCs_info_List(self, uid, csid, start, length):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # sql0 = "SELECT count(*) as num FROM cs WHERE csid=%s and cs_status=1"
                # # print(sql)
                # yield cursor.execute(sql0, uid)
                # datas2 = cursor.fetchone()
                sql = "SELECT users.uname,cs.uid,cs.csid,cs.cs_id,cs.cs_name,cs.cs_text,cs.utime " \
                      "FROM cs INNER JOIN users ON cs.uid = users.uid " \
                      "WHERE cs.csid=%s and cs.cs_status=1 ORDER BY cs.cs_id ASC "
                # print(sql)
                yield cursor.execute(sql, (csid,))
                datas = cursor.fetchall()
                if len(datas) > 0:
                    # datas.append({"allnum": datas2['num']})
                    return datas
                else:
                    return []

    # 新增问题
    @gen.coroutine
    def set_Cs(self, uid, csid, cs_name, cs_text):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.callproc('add_cs', (csid, uid, cs_name, cs_text, "@out_mflag"))
                    yield cursor.execute("select @out_mflag;")
                    row = cursor.fetchone()
                    if row['@out_mflag'] >= 0:
                        return row['@out_mflag']
                except Exception as err:
                    self.logger.error("[CsModel:set_Cs:INSERT]: %s" % err)
                    return -1

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
                    sql3 = "SELECT posts_type.posts_type_name_cn,posts.post_id,posts.post_status,posts.post_modified,posts.post_title," \
                           "posts.post_id " + from_str + sql + " ORDER BY posts.post_modified DESC limit %s, %s" % (int(start), int(length))
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
                sql = "SELECT posts.post_id,posts.post_content,posts.post_title," \
                      "posts.post_status,posts.post_modified,posts_type.posts_type_name_cn," \
                      "posts_type.posts_type_name_en FROM posts " \
                      "INNER JOIN posts_type_relationship ON posts.post_id = posts_type_relationship.post_id " \
                      "INNER JOIN posts_type ON posts_type_relationship.posts_type_id = posts_type.posts_type_id " \
                      "WHERE posts.post_id = %s"
                yield cursor.execute(sql, (id,))
                datas = cursor.fetchall()

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
                    datas[0]['pt_name_cn'] = tag_str_cn
                    datas[0]['pt_name_en'] = tag_str_en
                return datas