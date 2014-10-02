from httpcache import CachedHttp
from extract import extractCompetitions
import time

httpCache = 'd/html.kch'

allCompetitionsUrl = "http://www.kaggle.com/competitions/search?SearchVisibility=AllCompetitions&ShowActive=true&ShowCompleted=true&ShowProspect=true&ShowOpenToAll=true&ShowPrivate=true&ShowLimited=true"

downloadTimeoutSec = 1

def downloadCompetitions(http):
  html = http.get(allCompetitionsUrl)

  # we don't want to be banned by Kaggle, make 1 request per second
  t0 = time.time()
  for c in extractCompetitions(html):
    while time.time()-t0 < downloadTimeoutSec:
      time.sleep(0.1)

    print '  download [%s]' % c.url
    http.get(c.url)

def main():
  http = CachedHttp(httpCache)
  downloadCompetitions(http)

if __name__ == '__main__':
  main()
