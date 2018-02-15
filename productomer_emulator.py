#!/usr/bin/python3


import time

import ProtobufDevice_0000E002_pb2 as pb
from ProtocolProcessor import ProtocolProcessor
from spp_server import SPP

current_milli_time = lambda: int(round((time.time() - time.timezone) * 1000))


def dummy_print(*args, **kargs):
    pass


message = dummy_print

settings = pb.SettingsResponse()


class ProductomerEmulator:
    def __init__(self):
        self.connection = SPP(self.read_cb)
        self.processor = ProtocolProcessor(0x09)

    def read_cb(self, data):
        request = self.processor.ParceFromString(pb.Request(), data)

        response = self._createAnswer(request.id)

        error = False
        if request.HasField("writeSettings"):
            error |= self.processSettings(request, response)

        response.Global_status = pb.STATUS.Value('ERRORS_IN_SUBCOMMANDS') if error else pb.STATUS.Value('OK')

        self.send_data(self.processor.SerializeToString(response))

    def _createAnswer(self, request_id):
        response = pb.Response()
        response.id = request_id
        response.deviceID = pb.INFO.Value('PRODUCTOMER_2_ID')
        response.protocolVersion = pb.INFO.Value('PROTOCOL_VERSION')
        response.timestamp = current_milli_time()
        return response

    def send_data(self, data):
        self.connection.write_spp(data)

    def processSettings(self, req, resp):
        new_settings = req.writeSettings
        if new_settings.HasField("partNumber"):
            settings.partNumber = new_settings.partNumber

        resp.Settings.CopyFrom(settings)
        return False


def defaultSettings():
    settings.partNumber = 1
    settings.measureTimeT1 = 999
    settings.measureTimeT2 = 998
    settings.ReferenceFrequency = 1200000

    tcoefs = pb.TCoeffs()
    tcoefs.T0 = 0
    tcoefs.F0 = 0
    tcoefs.C.extend([1.0, 0.0, 0.0])

    settings.T1_Coeffs.CopyFrom(tcoefs)
    settings.T2_Coeffs.CopyFrom(tcoefs)

    settings.Enable_T1_Chanel = True
    settings.Enable_T2_Chanel = True

    settings.Show_T1_Freq = True
    settings.Show_T2_Freq = True


if __name__ == '__main__':
    defaultSettings()
    server = ProductomerEmulator()
    server.connection.start()
