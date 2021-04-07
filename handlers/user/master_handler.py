#coding=utf-8
#订单视图
import tornado
import config
import hashlib
import json
from tornado import gen
# from handlers.base.base_handler import BaseHandler
from datetime import datetime
from handlers.myredis.redis_class import RedisClass
from models.user.master_model import MasterModel

class MasterHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        get_class = self.get_argument('class')
        ukid = self.get_argument('ukid')
        AccountNumber = self.get_argument('f2')
        md5_from = self.get_argument('f5')
        copy_account = self.get_argument('f11', "")
        edit_flag = self.get_argument('f12', "")
        md5_from2 = self.get_argument('f13', "")
        MasterKey = self.get_argument('f14', "")
        pid = self.get_argument('s0', 0)
        echotext = ""
        if get_class=="edit":
            # 修改授权
            # 二次较检
            md5_str = AccountNumber + copy_account + str(config.TineMd5Info)
            str_md5 = hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()
            if str_md5 == md5_from2:
                # 信息验证成功，进行相关操作
                R = RedisClass()
                followid = yield R.chick_MD5_uaid(AccountNumber, md5_from, ukid)
                if followid > 0:
                    m_flag = yield R.chick_MaterAuthorize(followid, copy_account)
                    if edit_flag == "1" and m_flag == True:
                        echotext = "0,0,"
                    elif edit_flag == "0" and m_flag == False:
                        echotext = "0,0,"
                    else:
                        #需要修改授权
                        M = MasterModel()
                        flag = R.RH.hget(config.redis_master_uaid_Hash + str(followid), str(copy_account))

                        if flag == 1 or flag == "1":
                            mflag = yield M.setMaterAuthorize(followid, copy_account, 0)
                            if mflag == True:
                                R.RH.hset(config.redis_master_uaid_Hash + str(followid), str(copy_account), "0")
                                echotext = "1,0,"
                            else:
                                echotext = "-3,0,"
                        else:
                            # 判断超过授权数量
                            copy_max_num = yield M.get_copy_num(
                                R.RH.hgetall(config.redis_master_uaid_Hash + str(followid)))
                            master_max_num = yield M.getMaterCopyNum(pid, followid)
                            if copy_max_num >= master_max_num:
                                # 授权数量超过
                                echotext = "-6,0,"
                            else:
                                mflag = yield M.setMaterAuthorize(followid, copy_account, 1)
                                if mflag == True:
                                    R.RH.hset(config.redis_master_uaid_Hash + str(followid), str(copy_account), "1")
                                    echotext = "1,1,"
                                else:
                                    echotext = "-3,0,"
                else:
                    echotext = "-4,0,"
            else:
                echotext = "-5,0,"
        elif get_class=="apply":
            # 申请授权
            # 二次较检
            md5_str = AccountNumber + MasterKey + str(config.TineMd5Info)
            str_md5 = hashlib.md5(md5_str.encode(encoding='UTF-8')).hexdigest()
            if str_md5 == md5_from2:
                #信息验证成功
                R = RedisClass()
                uaid = yield R.chick_MD5_uaid(AccountNumber, md5_from, ukid)
                if uaid > 0:
                    M = MasterModel()
                    followid = yield R.get_Mater_uaid(MasterKey)
                    if followid == None:
                        mflag = False
                    else:
                        mflag = yield R.chick_MaterAuthorize(followid, uaid)
                    if mflag == True:
                        #已经授权
                        echotext = "2," + str(config.ERROR_TIME) + ",9947" + str(followid) + ","
                    else:
                        if followid != None:
                            # 有MasterKey的策略，进行申请操作
                            yield R.insert_master_uaid(MasterKey, followid)
                            #检查数据库
                            # print(followid,uaid)
                            yield M.checkMaterFollow(followid, uaid)
                            # 更新Redis
                            yield R.set_MaterFollow(followid, uaid, 0)
                            echotext = "1,0,"
                        else:
                            #无效MasterKey，找不到相关策略
                            echotext = "-3,0,"
                else:
                    echotext = "-4,0,"
            else:
                echotext = "-5,0,"

        self.write(echotext + config.StringEnd)
        self.finish()
