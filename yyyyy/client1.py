# coding = utf-8
#/usr/bin/python3
from yyyyy.tcp_client_chat import QQClient
if __name__ == '__main__':
    # 登录QQ、并和服务器建立连接、模拟登录
    qq = QQClient("13523456")
    # 开启聊天
    qq.chat("472759903")

