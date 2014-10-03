import sqlite3
import logging
from httpcache import CachedHttp
from extract import extractCompetitions, updateCompetition

logger = logging.getLogger(__name__)

httpCache = 'd/html.kch'

allCompetitionsUrl = "http://www.kaggle.com/competitions/search?SearchVisibility=AllCompetitions&ShowActive=true&ShowCompleted=true&ShowProspect=true&ShowOpenToAll=true&ShowPrivate=true&ShowLimited=true"

def updateSqlite(http, sqliteFile):
  html = http.get(allCompetitionsUrl)
  competitions = extractCompetitions(html)

  with sqlite3.connect(sqliteFile) as cn:
    cn.execute('create table if not exists competitions (id string, title string, blob blob)')
    for c in competitions:
      if c.id.startswith('/c/'):
        _updateCompetition(http.get(c.url), cn, c)

def _updateCompetition(html, cn, competition):
  updateCompetition(html, competition)
  rows = cn.execute('select id, title, blob from competitions where id == :id', {'id': competition.id})
  rows = list(rows)
  if len(rows) < 1:
    logger.debug('  [%s] insert' % competition.id)
    cn.execute(
        'insert into competitions (id, title, blob) values (:id, :title, :blob)',
        {'id': competition.id, 'title': competition.title, 'blob': _blob(competition)})
  else:
    row = rows[0]
    if _blob(competition) != row[2]:
      logger.debug('  [%s] update' % competition.id)
      cn.execute(
          'update competitions set title=:title, blob=:blob where id=:id',
          {'id': competition.id, 'title': competition.title, 'blob': _blob(competition)})
    else:
      logger.debug('  [%s] no change' % competition.id)

def _blob(competition):
  return sqlite3.Binary(competition.SerializeToString())

def main():
  http = CachedHttp(httpCache)
  sqliteFile = 'd/kaggle.sqlite'
  updateSqlite(http, sqliteFile)

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  main()
