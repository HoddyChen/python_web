#! /usr/bin/env python
# coding=utf-8
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from tornado import ioloop, gen, iostream

class Connection(object):
    clients = set()

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.on_close)
        self.read_message()
        print("A new user entered.", address)

    @gen.coroutine
    def read_message(self):
        try:
            msg = yield self._stream.read_until(bytes("\n", encoding="utf8"))
            if msg != "":
                # print("msg:%s" % msg)
                data = "your:" + str(msg, encoding="utf-8")
                yield self.broadcast_messages(data)
        except iostream.StreamClosedError:
            pass

    @gen.coroutine
    def broadcast_messages(self, data):
        try:
            for conn in Connection.clients:
                # print("conn:%s" % conn)
                print("User said:", data[:-1], conn._address)
                yield conn.send_message(data + "\n")
            print("----------------")
            yield self.read_message()
        except iostream.StreamClosedError:
            pass

    @gen.coroutine
    def send_message(self, data):
        try:
            yield self._stream.write(bytes(data,  encoding="utf8"))
        except iostream.StreamClosedError:
            pass

    @gen.coroutine
    def on_close(self):
        try:
            print("A user out.", self._address)
            Connection.clients.remove(self)
        except iostream.StreamClosedError:
            pass


class ChatServer(TCPServer):

    @gen.coroutine
    def handle_stream(self, stream, address):
        # stream.socket.settimeout(10)
        print("New connection :", address, stream)
        Connection(stream, address)
        print("connection num is:", len(Connection.clients))


if __name__ == '__main__':
    print("Server start ......")
    server = ChatServer()
    server.listen(9000)
    # server.bind(8888)# Forks multiple sub-processes
    # server.start(0)  # Forks multiple sub-processes
    # ioloop.IOLoop.instance().start()
    ioloop.IOLoop.current().start()
    # 3.
    # `add_sockets`: advanced
    # multi - process::
    #
    # sockets = bind_sockets(8888)
    # tornado.process.fork_processes(0)
    # server = TCPServer()
    # server.add_sockets(sockets)
    # IOLoop.current().start()