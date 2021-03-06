import os
from io import BytesIO
from select import select

from google.protobuf.internal.decoder import _DecodeSignedVarint as DecodeSignedVarint
from google.protobuf.internal.encoder import _EncodeSignedVarint as EncodeSignedVarint


class ProtocolProcessor:
    def __init__(self, magick):
        self.magick = magick.to_bytes(1, 'little')

    def isCorrectMagick(self, b):
        return b == self.magick

    def ParceFromString(self, message, data):
        magick = data[0].to_bytes(1, 'little')
        if not self.isCorrectMagick(magick):
            raise ValueError("Invalid magick ({:02X})".format(magick))
        length, offset = DecodeSignedVarint(data, 1)
        if length < 0 or length > 1500 or length > len(data) - offset:
            raise ValueError("length of message seems incorrect")
        message.ParseFromString(data[offset:offset + length])
        return message

    def ParceFromFile(self, message, fd):
        r, w, w = select([fd], [], [], 0)
        if len(r) == 0:
            return None
        magick = os.read(fd, 1)
        if not self.isCorrectMagick(magick):
            raise ValueError("Invalid magick ({:02X})".format(magick))
        buffer = os.read(fd, int(64 / 8))
        length, offset = DecodeSignedVarint(buffer, 0)
        if length < 0 or length > 1500:
            raise ValueError("length of message seems incorrect")
        buffer = buffer[offset:] + os.read(fd, length - len(buffer) + offset)
        message.ParseFromString(buffer)
        return message

    def SerializeToString(self, message):
        out = BytesIO()
        out.write(self.magick)
        EncodeSignedVarint(out.write, message.ByteSize(), False)
        out.write(message.SerializeToString())
        return out.getvalue()
