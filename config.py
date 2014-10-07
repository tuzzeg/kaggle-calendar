from protos import parseProtoText
from files import readFile
from data_pb2 import Config

def loadConfig(*files):
  conf = Config()
  for fileName in files:
    conf = parseProtoText(readFile(fileName), conf)
  return conf
