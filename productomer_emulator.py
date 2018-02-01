#!/usr/bin/python3


import time

import ProtobufDevice_0000E002_pb2 as pb
from spp_server import SPP

current_milli_time = lambda: int(round((time.time() - time.timezone) * 1000))


def dummy_print(*args, **kargs):
    pass


message = dummy_print


class ProductomerEmulator:
    def __init__(self):
        self.connection = SPP(self.read_cb)

    def read_cb(self, data):
        request = pb.Request()
        try:
            request.ParseFromString(data)
        except Exception:
            message('Request parce error')
            return

        response = pb.Response()
        response.id = request.id
        response.deviceID = pb.INFO.Value('PRODUCTOMER_2_ID')
        response.protocolVersion = pb.INFO.Value('PROTOCOL_VERSION')
        response.timestamp = current_milli_time()
        response.Global_status = pb.STATUS.Value('OK')

        self.send_data(response.SerializeToString())

    def send_data(self, data):
        self.connection.write_spp(data)


if __name__ == '__main__':
    server = ProductomerEmulator()
    server.connection.start()
