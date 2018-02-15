from io import BytesIO

from google.protobuf.internal.decoder import _DecodeSignedVarint as DecodeSignedVarint
from google.protobuf.internal.encoder import _EncodeSignedVarint as EncodeSignedVarint

import ProtobufDevice_0000E002_pb2 as pb
from ProtocolProcessor import ProtocolProcessor


def test_EncDecSVariant64():
    out = BytesIO()
    test_val = 42
    EncodeSignedVarint(out.write, test_val, False)
    v, pos = DecodeSignedVarint(out.getvalue(), 0)
    assert v == test_val


def test_serialise():
    req = pb.Request()
    req.id = 0
    req.deviceID = 0
    req.protocolVersion = pb.INFO.Value('PROTOCOL_VERSION')

    magick = 0x1e

    processor = ProtocolProcessor(magick)
    msg_dressed = processor.SerializeToString(req)

    req_data = req.SerializeToString()
    length, offest = DecodeSignedVarint(msg_dressed, 1)

    assert msg_dressed[0] == magick
    assert length == len(req_data)
    assert msg_dressed[offest:] == req_data


def test_deserialise():
    req = pb.Request()
    req.id = 0
    req.deviceID = pb.INFO.Value('PRODUCTOMER_2_ID')
    req.protocolVersion = pb.INFO.Value('PROTOCOL_VERSION')

    processor = ProtocolProcessor(0x31)
    msg_dressed = processor.SerializeToString(req)
    result = processor.ParceFromString(pb.Request(), msg_dressed)

    assert result.id == req.id
    assert result.deviceID == req.deviceID
    assert result.protocolVersion == req.protocolVersion
