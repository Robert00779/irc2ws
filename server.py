# coding: utf-8

import logging
import socket

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.web import Application
from tornado.websocket import WebSocketHandler


class WS2IRCBridge(WebSocketHandler):
    def open(self, host='irc.freenode.net', port=None):
        port = int(port or 6667)
        self.sock = IOStream(socket.socket(socket.AF_INET,
                                           socket.SOCK_STREAM, 0))
        self.sock.connect((host, port), self.sock_loop)
        logging.debug("Request received for %s:%d", host, port)

    def sock_loop(self, data=None):
        if data:
            self.write_message(data)

        if self.sock.closed():
            self.close()
            logging.debug("IRC socket closed. Closing active WebSocket too.")
        else:
            self.sock.read_until("\r\n", self.sock_loop)

    def on_message(self, message):
        self.sock.write(message.encode('utf-8') + "\r\n")

    def on_close(self):
        self.sock.close()
        logging.debug("Client closed the WebSocket.")


if __name__ == "__main__":
    settings = dict(auto_reload=True)
    app = Application([(r'/([^:]*):?(\d*)$', WS2IRCBridge)],
                      **settings)
    app.listen(1988)
    IOLoop.instance().start()
