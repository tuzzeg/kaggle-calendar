from data_pb2 import Config
from google.protobuf import text_format

def loadConfig(*files):
  conf = Config()
  for fileName in files:
    with open(fileName) as f:
      text_format.Merge(f.read(), conf)
  return conf
