# coding = utf-8
# /usr/bin/python3
def read_chat(socket):  # 谁发送的、发送的内容
    """
    读取别人发送过来的数据
    :param socket:
    :return:
    """
    while True:
        try:
            msg = socket.recv(1024).decode()
            # 将接收到的信息、打印到控制台上
            print(msg)
        except ConnectionResetError:
            print("服务器连接失败、请重新连接~")
            break


def write_chat(socket, to_qq):  # 谁发的、发给谁的、内容
    """
    发送信息给to_qq
    :param socket:
    :param to_qq:
    :return:
    """
    while True:
        msg = input()
        # 准备发送给服务器的内容
        msg = f"{to_qq}:{msg}"
        # 将信息发送给服务器
        try:
            socket.send(msg.encode())
        except ConnectionResetError:
            print("服务器连接失败、请重新连接~")
            break


def server_chat(socket, socket_mapping):
    """
    服务器处理数据、并实现两个客户端的交互
    :param socket:
    :param socket_mapping:
    :return:
    """
    # 接收客户端的身份、并进行存储
    qq = socket.recv(1024).decode()
    # 存储身份(这里也可以实现不允许同一账户多次登录)
    socket_mapping[qq] = socket
    # 给所有socket 显示 该用户上线了
    for k, v in socket_mapping.items():
        v.send(f"【{qq}】上线了".encode())

    # 开启循环、用来不断的进行转发数据
    while True:
        try:
            # 接收客户端发送的信息
            data = socket.recv(1024).decode()
            to_qq, msg = data.split(":", 1)
            # 将信息转发给 to_qq 对应的客户端
            to_socket = socket_mapping[to_qq]
            # 将信息发送给 to_socket
            to_socket.send(f"{qq}:{msg}".encode())
        except ConnectionResetError:
            # 该客户端离线了
            socket_mapping.pop(qq)
            # 提示所有的客户端、该用户下线了
            for k, v in socket_mapping.items():
                v.send(f"【{qq}】下线了".encode())
            # 退出循环
            break
        except KeyError:
            # 该用户不在线、提示fqq,您的好友不在线
            socket.send(f"您的好友【{to_qq}】不在线".encode())
