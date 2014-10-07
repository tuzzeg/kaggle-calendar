from cmd import Command
from extract import extractCompetitions
from httpcache import FetchStorage
from functools import partial
import cmd
import logging
import time

logger = logging.getLogger(__name__)

downloadTimeoutSec = 1

HOUR=3600
WEEK=7*24*HOUR

def updateDownloads(conf):
  allCompetitionsUrl = conf.downloader.competitionsUrl
  storage = FetchStorage(conf.downloader.storageFile, fetchIntervalSec=1)

  page = storage.get(allCompetitionsUrl, cachedTime=HOUR)

  for c in extractCompetitions(page.contents):
    storage.get(c.url, cachedTime=WEEK)

def fetchAll(command, args, conf):
  updateDownloads(conf)

commands = {
  'fetch-all': partial(Command, fetchAll)
}

if __name__ == '__main__':
  cmd.main(commands)
