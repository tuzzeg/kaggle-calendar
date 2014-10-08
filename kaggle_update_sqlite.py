from data_pb2 import Competition, COMPETITION
from extract import extractCompetitions, updateCompetition
from functools import partial
from httpcache import FetchStorage
from lib import cmd
from lib.cmd import Command
from lib.protos import parseProto
import logging
import sqlite3
import urlparse

logger = logging.getLogger(__name__)

def _sync(conf):
  storage = FetchStorage(conf.downloader.storageFile, readOnly=True)
  sqliteFile = conf.sqliteSyncer.sqliteFile

  pages = list(storage.values())

  with sqlite3.connect(sqliteFile) as cn:
    cn.execute('create table if not exists competitions (id string, title string, blob blob)')
    for page in pages:
      pageType = _pageType(page)
      logger.debug('[%s] pageType=%s' % (page.url, pageType))
      if pageType == COMPETITION:
        _updateCompetition(cn, page)

def _pageType(page):
  url = urlparse.urlparse(page.url)
  if url.path.startswith('/c/') and len(url.query) == 0:
    return COMPETITION
  else:
    return None

def _updateCompetition(cn, page):
  competition = Competition(url=page.url)
  updateCompetition(page.contents, competition)

  rows = cn.execute('select id, title, blob from competitions where id == :id', {'id': competition.id})
  rows = list(rows)
  if len(rows) < 1:
    logger.debug('[%s] insert' % competition.id)
    cn.execute(
        'insert into competitions (id, title, blob) values (:id, :title, :blob)',
        {'id': competition.id, 'title': competition.title, 'blob': _blob(competition)})
  else:
    row = rows[0]
    if _blob(competition) != row[2]:
      logger.debug('[%s] update' % competition.id)
      cn.execute(
          'update competitions set title=:title, blob=:blob where id=:id',
          {'id': competition.id, 'title': competition.title, 'blob': _blob(competition)})
    else:
      logger.debug('[%s] no change' % competition.id)

def _blob(competition):
  return sqlite3.Binary(competition.SerializeToString())

def sync(command, args, conf):
  _sync(conf)

commands = {
  'sync': partial(Command, sync)
}

if __name__ == '__main__':
  cmd.main(commands)
