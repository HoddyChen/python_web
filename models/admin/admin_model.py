# coding = utf-8
from tornado import gen
import logging
from libs.db.dbsession import pool
import hashlib
import datetime
import config
import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import random

logger = logging.getLogger('Main')
class ManagerModel():

    @gen.coroutine
    def chickLoginPass(self, mail, password):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                password_md5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
                sql = "SELECT users.uid, users.uname, users.faceurl,admin_relationship.admin_id  FROM users INNER JOIN admin_relationship ON users.uid = admin_relationship.uid " \
                      "WHERE (users.phone='%s' OR users.email='%s') AND admin_relationship.admin_pass='%s' AND admin_relationship.admin_status=1"
                # print(sql% (mail, mail, password_md5))
                yield cursor.execute(sql % (mail, mail, password_md5))
                datas = cursor.fetchone()
        return datas

    @gen.coroutine
    def getUmail(self, uid):
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                # users['ptname']db.cursor(MySQLdb.cursors.DictCursor)
                sql = "SELECT uid, email FROM users WHERE uid=%s"
                # print(sql% (mail, mail, password_md5))
                yield cursor.execute(sql % (uid,))
                datas = cursor.fetchone()
        return datas['email']