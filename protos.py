from google.protobuf import text_format

def parseProto(buf, proto):
  proto.ParseFromString(buf)
  return proto

def parseProtoText(text, proto):
  text_format.Merge(text, proto)
  return proto
