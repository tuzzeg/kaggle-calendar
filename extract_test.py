import unittest
from kaggle_list import extractCompetitions, updateCompetition, extractDates
from data_pb2 import Competition
from datetime import datetime
import time

class ExtractorTest(unittest.TestCase):
  def test_extract_list(self):
    html = readFile('test/comp_list.html')
    competitions = list(extractCompetitions(html))
    competitions = {c.id:c for c in competitions}

    self.assertEquals(152, len(competitions))
    self.assertTrue('/c/mdm' in competitions)
    self.assertTrue('/c/detecting-insults-in-social-commentary' in competitions)

  def test_extract_comp(self):
    html = readFile('test/comp_mdm.html')
    c = Competition(id='/c/mdm')

    updateCompetition(html, c)

    self.assertEquals('Mapping Dark Matter', c.title)
    self.assertDate('Mon, 23 May 2011 13:42:00 +0000', c.start)
    self.assertDate('Thu, 18 Aug 2011 00:00:00 +0000', c.end)

  def test_extract_dates(self):
    dates = extractDates('''Started: 1:42 pm, Monday 23 May 2011 UTC
      Ended: 12:00 am, Thursday 18 August 2011 UTC (86 total days)''')
    dates = list(dates)

    self.assertEqual(2, len(dates))
    self.assertEqual([('started', datetime(2011, 5, 23, 13, 42)), ('ended', datetime(2011, 8, 18, 0, 0))], dates)

  def assertDate(self, dateStr, dt):
    dtStr = time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime(dt.timestamp_utc))
    self.assertEquals(dateStr, dtStr)

def readFile(fileName):
  with open(fileName) as f:
    return f.read()

if __name__ == '__main__':
  unittest.main()
