import os.path
import urlparse
from collections import namedtuple
from bs4 import BeautifulSoup
from httpcache import CachedHttp
import re
from datetime import datetime
from data_pb2 import Competition, Date
import calendar

httpCache = 'd/html.kch'

allCompetitionsUrl = "http://www.kaggle.com/competitions/search?SearchVisibility=AllCompetitions&ShowActive=true&ShowCompleted=true&ShowProspect=true&ShowOpenToAll=true&ShowPrivate=true&ShowLimited=true"

def extractCompetitions(html):
  doc = BeautifulSoup(html)
  for el in doc.body.find_all('div', attrs={'class': 'competition-details'}):
    el_p = el.find('p', attrs={'class': 'competition-summary'})
    el_p_a = el_p.find('a')

    id = el_p_a['href']
    url = urlparse.urljoin('http://kaggle.com', id)
    yield Competition(id=id, url=url)

class ReFactory(object):
  def __init__(self, terminals):
    self._terminals = terminals

  def build(self, pattern):
    return re.compile(self._expand(pattern), re.I)

  def _expand(self, pattern):
    _re = re.compile('<([^>]*)>', re.I)
    return _re.sub(lambda m: self._terminals.get(m.group(1), m.group()), pattern)

# 1:42 pm, Monday 23 May 2011 UTC
_reF = ReFactory(
  terminals = {
    'D2': '[0-9]{,2}',
    'D4': '[0-9]{,4}',
    'AM': '(?:pm|am)',
    'WEEKDAYS': '(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
    'MONTHS': '(?:january|february|march|april|may|june|july|august|september|october|november|october|december)'
  }
)
def extractDates(text):
  # 1:42 pm, Monday 23 May 2011 UTC
  _re = _reF.build('(started|ended): (<D2>:<D2> <AM>, <WEEKDAYS> <D2> <MONTHS> <D4> UTC)')
  for typ, dateStr in _re.findall(text):
    date = datetime.strptime(dateStr, '%I:%M %p, %A %d %B %Y %Z')
    yield (typ.lower(), date)

def updateCompetition(html, competition):
  doc = BeautifulSoup(html)

  _updateCompetitionTitle(doc, competition)
  _updateCompetitionDates(doc, competition)

def _updateCompetitionTitle(doc, competition):
  el = doc.body.find('div', attrs={'id': 'comp-header-details'})
  el_h1 = el.find('h1')
  if el_h1:
    competition.title = el_h1.text.strip()

def _updateCompetitionDates(doc, competition):
  el = doc.body.find('p', attrs={'id': 'end-time-note'})
  dates = dict(extractDates(el.text))

  if 'started' in dates:
    _setDate(competition.start, dates['started'])
  if 'ended' in dates:
    _setDate(competition.end, dates['ended'])

def _setDate(proto, dt):
  proto.timestamp_utc = calendar.timegm(dt.utctimetuple())

def _dumpCompetitions(http):
  html = http.get(allCompetitionsUrl)
  for c in extractCompetitions(html):
    print c

def _dumpCompetition(http, url):
  html = http.get(url)

  c = Competition(id='1')
  updateCompetition(html, c)

  print c

def main():
  http = CachedHttp(httpCache)

  # _dumpCompetitions(http)
  _dumpCompetition(http, 'http://www.kaggle.com/c/mdm')

if __name__ == '__main__':
  main()
