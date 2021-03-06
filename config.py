from lib.protos import parseProtoText
from lib.files import readFile
from data_pb2 import Config

def loadConfig(*files):
  conf = Config()
  for fileName in files:
    conf = parseProtoText(readFile(fileName), conf)
  return conf
