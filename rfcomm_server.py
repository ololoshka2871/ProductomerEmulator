#!/usr/bin/python3

from spp_server import SPP


class MyServer:
    def __init__(self):
        self.server = SPP(self.onRessive)

    def onRessive(self, data):
        print('>>'.format(data))

    def sendData(self, data):
        self.server.write_spp(data)

    def start(self):
        self.server.start()


if __name__ == '__main__':
    MyServer().start()
