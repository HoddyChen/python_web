# coding = utf-8
#/usr/bin/python3
import socket
import threading
import yyyyy.chat as chat

if __name__ == '__main__':
    # 初始化socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定IP地址和端口
    server.bind(("localhost", 8888))
    # 设置最大监听数
    server.listen(5)
    # 设置一个字典，用来保存每一个客户端的连接 和 身份信息
    socket_mapping = {}
    # 开启准备等待获取客户端的链接
    while True:
        sc, addr = server.accept()
        # 为每一个客户端开启一个线程、保证程序的高效运行
        threading.Thread(target=chat.server_chat, args=(sc, socket_mapping)).start()
