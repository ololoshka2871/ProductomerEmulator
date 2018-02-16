#!/usr/bin/python3


import math
import time
from functools import reduce

import ProtobufDevice_0000E002_pb2 as pb
from ProtocolProcessor import ProtocolProcessor
from spp_server import SPP

current_milli_time = lambda: int(round((time.time() - time.timezone) * 1000))


def dummy_print(*args, **kargs):
    pass


message = print

settings = pb.SettingsResponse()


class ProductomerEmulator:
    def __init__(self):
        self.connection = SPP(self.read_cb)
        self.processor = ProtocolProcessor(0x09)

    def read_cb(self, fd):
        message("Read called at : {}".format(time.time()))
        while True:
            request = self.processor.ParceFromFile(pb.Request(), fd)
            if not request:
                break

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
        error = False

        new_settings = req.writeSettings
        if new_settings.HasField("partNumber"):
            settings.partNumber = new_settings.partNumber
        if new_settings.HasField("measureTimeT1"):
            if 20 < new_settings.measureTimeT1 < 2000:
                settings.measureTimeT1 = new_settings.measureTimeT1
            else:
                error |= True
        if new_settings.HasField("measureTimeT2"):
            if 20 < new_settings.measureTimeT2 < 2000:
                settings.measureTimeT2 = new_settings.measureTimeT2
            else:
                error |= True

        if new_settings.HasField("ReferenceFrequency"):
            if 11999500 < new_settings.ReferenceFrequency < 12000500:
                settings.ReferenceFrequency = new_settings.ReferenceFrequency
            else:
                error |= True

        if new_settings.HasField("Enable_T1_Chanel"):
            settings.Enable_T1_Chanel = new_settings.Enable_T1_Chanel
        if new_settings.HasField("Enable_T2_Chanel"):
            settings.Enable_T2_Chanel = new_settings.Enable_T2_Chanel
        if new_settings.HasField("Show_T1_Freq"):
            settings.Show_T1_Freq = new_settings.Show_T1_Freq
        if new_settings.HasField("Show_T2_Freq"):
            settings.Show_T2_Freq = new_settings.Show_T2_Freq

        if new_settings.HasField("T1_Coeffs"):
            if self.check_coeffs(new_settings.T1_Coeffs):
                settings.T1_Coeffs.CopyFrom(new_settings.T1_Coeffs)
            else:
                error |= True
        if new_settings.HasField("T2_Coeffs"):
            if self.check_coeffs(new_settings.T2_Coeffs):
                settings.T2_Coeffs.CopyFrom(new_settings.T2_Coeffs)
            else:
                error |= True

        resp.Settings.CopyFrom(settings)

        message("Processing SettingsRequest.. " + ("error" if error else "success"))

        return error

    def check_coeffs(self, coeffs):
        return (not math.isnan(coeffs.F0)) and (not math.isnan(coeffs.T0)) and \
               (len(coeffs.C) == 3) and \
               not reduce(lambda a, v: a or v, map(math.isnan, coeffs.C))


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
