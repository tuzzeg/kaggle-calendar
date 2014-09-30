[2014-09-29] Scrape Kaggle.com and create calendar events

- KaggleScraper
  - parse competitions list
  - parse competition page
    - extract start/end dates
    - extract title
  - sync with sqlite
- KaggleCalendarUpdater
  - add new events, update existing (if changed)
