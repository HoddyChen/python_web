# -*- coding: utf-8 -*-
import os
import glob
import re
# os.chdir('d:\\QLDownload')
#D:\OneDrive - ‎\one\python_project\socket_python\static\languages\en_US\LC_MESSAGES
#\templates\user
type = input("输入要执行的命令，1、生成PO，2、生成MO")
# 模板路径
path = '../../mo_tool'
tm_path = '../templates/user'
# # 得到当前工作路径
# path0 = os.getcwd()
if type == "1":
    os.chdir(tm_path)

    # 判断log目录是不是存2在
    par = re.compile('(.*?)_')
    filename_list = glob.glob(r'*.html')
    #
    for textname in filename_list:

        filename = os.path.splitext(textname)
        if filename[0] != "mode_login":
            continue
        print(textname)
        try:
            os.system("python pygettext.py -a -o " + filename[0] + ".po " + textname)
            print("python pygettext.py -a -o " + filename[0] + ".po " + textname)
        except Exception as e:
            print("err: %s" % textname)
elif type == "2":
    # 生成mo
    # 切换目录
    # os.chdir("../mo_tool")
    print("python msgfmt.py -o en_US.mo mode_login.po")
    os.system("python  msgfmt.py -o en_US.mo mode_login.po")
