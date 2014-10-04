import re
import urlparse
import calendar
from bs4 import BeautifulSoup
from datetime import datetime
from data_pb2 import Competition, Date

class ReFactory(object):
  '''Build regex defined in grammar-like fashion.'''

  def __init__(self, terminals):
    self._terminals = terminals

  def build(self, pattern):
    return re.compile(self._expand(pattern), re.I)

  def _expand(self, pattern):
    _re = re.compile('<([^>]*)>', re.I)
    return _re.sub(lambda m: self._terminals.get(m.group(1), m.group()), pattern)

def extractCompetitions(html):
  '''Extract competition from kaggle.com/competitions page.'''
  doc = BeautifulSoup(html)
  for el in doc.body.find_all('div', attrs={'class': 'competition-details'}):
    el_p = el.find('p', attrs={'class': 'competition-summary'})
    el_p_a = el_p.find('a')

    id = el_p_a['href']
    url = urlparse.urljoin('http://www.kaggle.com', id)
    yield Competition(id=id, url=url)

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
  _re = _reF.build('(started|ended|ends): (<D2>:<D2> <AM>, <WEEKDAYS> <D2> <MONTHS> <D4> UTC)')
  for typ, dateStr in _re.findall(text):
    date = datetime.strptime(dateStr, '%I:%M %p, %A %d %B %Y %Z')
    yield (typ.lower(), date)

def updateCompetition(html, competition):
  '''
  Parse competition page and extract such information as
  - Title, description
  - Reward ($$)
  - Competition type (knowledge, limited)
  '''
  doc = BeautifulSoup(html)

  _updateCompetitionTitle(doc, competition)
  _updateCompetitionDescription(doc, competition)
  _updateCompetitionDates(doc, competition)
  _updateCompetitionAttributes(doc, competition)
  _updateCompetitionLimited(doc, competition)

def _updateCompetitionTitle(doc, competition):
  el = doc.body.find('div', attrs={'id': 'comp-header-details'})
  if not el:
    return
  el_h1 = el.find('h1')
  if not el_h1:
    return
  competition.title = el_h1.text.strip()

def _updateCompetitionDescription(doc, competition):
  el = doc.body.find('h1', attrs={'class': 'page-name'})
  if not el:
    return
  competition.description = el.text.strip()

def _updateCompetitionAttributes(doc, competition):
  el = doc.body.find('div', attrs={'id': 'comp-header-details'})
  if not el:
    return
  el_h2 = el.find('h2')
  if not el_h2:
    return
  attrs = el_h2.text

  reward = re.findall('\$\\b([0-9,]+)\\b', attrs, re.I)
  if len(reward) == 1:
    competition.reward_usd = int(reward[0].replace(',', ''))
  if re.search('(kudos|knowledge)', attrs, re.I):
    competition.attributes.append(Competition.KNOWLEDGE)

def _updateCompetitionLimited(doc, competition):
  el = doc.body.find('div', attrs={'id': 'limited-notice'})
  if el:
    competition.attributes.append(Competition.LIMITED)

def _updateCompetitionDates(doc, competition):
  el = doc.body.find('p', attrs={'id': 'end-time-note'})
  if not el:
    return
  dates = dict(extractDates(el.text))

  if 'started' in dates:
    _setDate(competition.start, dates['started'])
  if 'ended' in dates:
    _setDate(competition.end, dates['ended'])
  if 'ends' in dates:
    _setDate(competition.end, dates['ends'])

def _setDate(proto, dt):
  proto.timestamp_utc = calendar.timegm(dt.utctimetuple())
