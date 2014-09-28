import os.path
import urlparse
from collections import namedtuple
from bs4 import BeautifulSoup
from httpcache import CachedHttp
import re
from datetime import datetime

httpCache = 'd/html.kch'

allCompetitionsUrl = "http://www.kaggle.com/competitions/search?SearchVisibility=AllCompetitions&ShowActive=true&ShowCompleted=true&ShowProspect=true&ShowOpenToAll=true&ShowPrivate=true&ShowLimited=true"

Competition = namedtuple('Competetion', ['url'])
def extractCompetitions(html):
  doc = BeautifulSoup(html)
  for el in doc.body.find_all('div', attrs={'class': 'competition-details'}):
    el_p = el.find('p', attrs={'class': 'competition-summary'})
    el_p_a = el_p.find('a')
    yield Competition(url=el_p_a['href'])

def printCompetitions(http):
  html = http.get(allCompetitionsUrl)
  for c in extractCompetitions(html):
    url = urlparse.urljoin('http://kaggle.com', c.url)
    print url
    #html = http.get(url)
    #print html

def parseCompetition(http, url):
  html = http.get(url)
  doc = BeautifulSoup(html)

  for el in doc.body.find_all('p', attrs={'id': 'end-time-note'}):
    print el.text

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

def main():
  http = CachedHttp(httpCache)

  # printCompetitions(http)

  parseCompetition(http, 'http://www.kaggle.com/c/mdm')

if __name__ == '__main__':
  main()
