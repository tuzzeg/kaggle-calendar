import os.path
import urllib2
from collections import namedtuple
from bs4 import BeautifulSoup

url = "http://www.kaggle.com/competitions/search?SearchVisibility=AllCompetitions&ShowActive=true&ShowCompleted=true&ShowProspect=true&ShowOpenToAll=true&ShowPrivate=true&ShowLimited=true"

def readHtml(url, cacheFile=None):
  if not cacheFile is None and os.path.isfile(cacheFile):
    with open(cacheFile) as f:
      return f.read()

  resp = urllib2.urlopen(url)
  html = resp.read()
  if not cacheFile is None:
    with open(cacheFile, 'w+') as f:
      f.write(html)
  return html

Competition = namedtuple('Competetion', ['url'])
def extractCompetitions(html):
  doc = BeautifulSoup(html)
  for el in doc.body.find_all('div', attrs={'class': 'competition-details'}):
    el_p = el.find('p', attrs={'class': 'competition-summary'})
    el_p_a = el_p.find('a')
    yield Competition(url=el_p_a['href'])

def main():
  html = readHtml(url, 'competition.html')
  for c in extractCompetitions(html):
    print c

if __name__ == '__main__':
  main()
