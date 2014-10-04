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
  allCompetitionsUrl = conf.downloaderConfig.competitionsUrl
  storage = FetchStorage(conf.downloaderConfig.storageFile)

  page = storage.get(allCompetitionsUrl, forceAfter=HOUR)

  # we don't want to be banned by Kaggle, make 1 request per second
  t0 = time.time()
  for c in extractCompetitions(page.contents):
    while time.time()-t0 < downloadTimeoutSec:
      time.sleep(0.1)

    logger.debug('download [%s]' % c.url)
    storage.get(c.url, forceAfter=WEEK)

def fetchAll(command, args, conf):
  updateDownloads(conf)

commands = {
  'fetch-all': partial(Command, fetchAll)
}

if __name__ == '__main__':
  cmd.main(commands)
