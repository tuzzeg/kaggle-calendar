import urllib2
from kyotocabinet import DB

class CachedHttp(object):
  def __init__(self, fileName):
    db = DB()
    if not db.open(fileName, DB.OWRITER | DB.OCREATE):
      raise Exception, 'Could not open db, %s' % fileName
    self._db = db

  def get(self, url):
    html = self._db.get(url)
    if html is None:
      resp = urllib2.urlopen(url)
      html = resp.read()
      self._db.set(url, html)
    return html

  def close(self):
    if not self._db is None:
      self._db.close()
      self._db = None

  def __enter__(self):
    return self

  def __exit__(self, type, value, tb):
    self.close()
