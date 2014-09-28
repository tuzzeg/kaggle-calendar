import unittest
from kaggle_list import extractDates
from datetime import datetime

class ExtractorTest(unittest.TestCase):
  def test_extract_dates(self):
    dates = extractDates('''Started: 1:42 pm, Monday 23 May 2011 UTC
      Ended: 12:00 am, Thursday 18 August 2011 UTC (86 total days)''')
    dates = list(dates)

    self.assertEqual(2, len(dates))
    self.assertEqual([('started', datetime(2011, 5, 23, 13, 42)), ('ended', datetime(2011, 8, 18, 0, 0))], dates)

if __name__ == '__main__':
  unittest.main()
