[2014-09-29] Scrape Kaggle.com and create calendar events

+ KaggleScraper
  + parse competitions list
  + parse competition page
    + extract start/end dates
    + extract title
  + sync with sqlite
- KaggleCalendarUpdater
  + add new events, update existing (if changed)
- Generate iCal
- Launch
  + Special account
  - Static site
  - Run downloader, updater periodically
  - Alerts if upload/sync/download stalled

[2014-10-08]
- Updaters (sqlite, calendar): update only competitions changed since last sync
- Log updated/added/unmodified
- Save logs in file, logrotate/gzip
- Merge `kaggle_*.py` into one script

[2014-10-20]
- Post about new Kaggle competitions
  - to email list
- Better visualization of KaggleCompetition (timeline)
