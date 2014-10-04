import time
import urllib2
import email.utils
import logging
from kyotocabinet import DB
from data_pb2 import FetchedPage

logger = logging.getLogger(__name__)

class FetchStorage(object):
  def __init__(self, fileName):
    db = DB()
    if not db.open(fileName, DB.OWRITER | DB.OCREATE):
      raise Exception, 'Could not open db, %s' % fileName
    self._db = db

  def get(self, url, forceAfter=None):
    storedBytes = self._db.get(url)

    if storedBytes is None:
      page = self._download(url)
      updated = page
      logger.debug('url=%s downloaded' % (url))
    else:
      page = FetchedPage()
      page.ParseFromString(storedBytes)

      t0 = time.time()
      logger.debug('url=%s fetched, timestamp=%s' % (url, page.timestamp))
      if forceAfter and t0-page.timestamp < forceAfter:
        updated = self._download(url, ifModifiedSince=page.timestamp)
        if updated:
          page = updated
      else:
        updated = self._download(url)

    if not updated is None:
      self._db.set(url, updated.SerializeToString())

    return page

  def _download(self, url, ifModifiedSince=None):
    req = urllib2.Request(url)
    if ifModifiedSince:
      req.add_header("If-Modified-Since", email.utils.formatdate(ifModifiedSince))
    try:
      response = urllib2.urlopen(req)
      page = FetchedPage()
      page.url = url
      page.contents = response.read()
      page.timestamp = int(time.time())
      return page

    except urllib2.HTTPError, e:
      if e.code == 304:
        # The resourse was not modified
        return None
      else:
        raise e

  def close(self):
    if not self._db is None:
      self._db.close()
      self._db = None

  def __enter__(self):
    return self

  def __exit__(self, type, value, tb):
    self.close()
