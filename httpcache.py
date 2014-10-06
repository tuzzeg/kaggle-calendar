import time
import urllib2
import email.utils
import logging
import random
from kyotocabinet import DB
from data_pb2 import FetchedPage

logger = logging.getLogger(__name__)

class FetchStorage(object):
  def __init__(self, fileName, fetchIntervalSec=1):
    db = DB()
    if not db.open(fileName, DB.OWRITER | DB.OCREATE):
      raise Exception, 'Could not open db, %s' % fileName
    self._db = db

    self._rateLimit = RateLimit(fetchIntervalSec)

  def get(self, url, cachedTime=None):
    storedBytes = self._db.get(url)

    if storedBytes is None:
      page = self._download(url)
      self._db.set(url, page.SerializeToString())
    else:
      page = FetchedPage()
      page.ParseFromString(storedBytes)

      t0 = time.time()
      if cachedTime is None or int((1+random.random())*cachedTime) < t0-page.timestamp:
        page = self._download(url)
        self._db.set(url, page.SerializeToString())
      else:
        logger.debug('[%s] cached, t=%s' % (url, t0-page.timestamp))

    return page

  def _download(self, url):
    # wait to balance QPS
    self._rateLimit.wait()

    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    logger.debug('[%s] fetched' % (url))

    page = FetchedPage()
    page.url = url
    page.contents = response.read()
    page.timestamp = int(time.time())
    return page

  def close(self):
    if not self._db is None:
      self._db.close()
      self._db = None

  def __enter__(self):
    return self

  def __exit__(self, type, value, tb):
    self.close()

class RateLimit(object):
  def __init__(self, fetchIntervalSec=1):
    self._interval = fetchIntervalSec
    self.t0 = time.time()

  def wait(self):
    while time.time()-self.t0 < self._interval:
      time.sleep(0.1)
    self.t0 = time.time()
