import unittest
import time
from extract import extractCompetitions, updateCompetition, extractDates
from data_pb2 import Competition
from datetime import datetime

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
    self.assertEquals(
        'Supported by NASA and the Royal Astronomical Society. ' +
        'A cosmological image analysis competition to measure the ' +
        'small distortion in galaxy images caused by dark matter. ' +
        'The prize is an expenses paid visit to the NASA Jet Propulsion ' +
        'Laboratory (JPL).', c.description)
    self.assertEquals(frozenset(), frozenset(c.attributes))
    self.assertEquals(3000, c.reward_usd)

  def test_extract_overfitting(self):
    html = readFile('test/comp_overfitting.html')
    c = Competition(id='/c/overfitting')

    updateCompetition(html, c)

    self.assertEquals('Don\'t Overfit!', c.title)
    self.assertDate('Mon, 28 Feb 2011 00:00:00 +0000', c.start)
    self.assertDate('Sun, 15 May 2011 00:00:00 +0000', c.end)

    self.assertEquals(
        'With nearly as many variables as training cases, ' +
        'what are the best techniques to avoid disaster?',
        c.description)
    self.assertEquals(frozenset(), frozenset(c.attributes))
    self.assertEquals(500, c.reward_usd)

  def test_extract_sentiment(self):
    html = readFile('test/comp_sentiment.html')
    c = Competition(id='/c/sentiment-analysis-on-movie-reviews')

    updateCompetition(html, c)

    self.assertEquals('Sentiment Analysis on Movie Reviews', c.title)
    self.assertTrue(c.HasField('start'))
    self.assertTrue(c.HasField('end'))
    self.assertDate('Fri, 28 Feb 2014 16:54:00 +0000', c.start)
    self.assertDate('Sat, 28 Feb 2015 23:59:00 +0000', c.end)

    self.assertEquals(
        'Classify the sentiment of sentences from the Rotten Tomatoes dataset',
        c.description)
    self.assertEquals(frozenset([Competition.KNOWLEDGE]), frozenset(c.attributes))
    self.assertFalse(c.HasField('reward_usd'))

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
