#coding=utf-8
# 标签生成
import tornado
from tornado.ioloop import IOLoop
from libs.db.dbsession import pool
from tornado import gen
import logging

logger = logging.getLogger('Main')
class Tags_Handler():

    @gen.coroutine
    def echoTagsAll(self, subject_id, subject_type):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql2 = "SELECT tags_text_,tags_text_en,tags_id FROM echo_subject_tags WHERE subject_id = %s AND subject_type = %s AND st_status = 1"
                    # print(sql2,subject_id)
                    yield cursor.execute(sql2, (subject_id, subject_type))
                    datas = cursor.fetchall()
                    return datas
                except Exception as err:
                    logger.error("[echoTagsAll] %s" % err)
                    return []

    @gen.coroutine
    def echoTagsRecent(self, subject_id, subject_type):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    sql2 = """SELECT COUNT(tags_id) AS yy,tags_text_,tags_text_en,tags_id
                        FROM echo_subject_tags
                        WHERE subject_type = %s AND st_status = 1
                        GROUP BY tags_id
                        ORDER BY
                        yy DESC LIMIT 0, 20"""
                    # print(sql2,subject_id)
                    yield cursor.execute(sql2, subject_type)
                    datas = cursor.fetchall()
                    return datas
                except Exception as err:
                    logger.error("[echoTagsRecent] %s" % err)
                    return []