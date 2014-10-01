import argparse
import sqlite3
import base64
import time
from google.protobuf import text_format

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.file import Storage
from oauth2client import tools

from data_pb2 import Competition, Date, CalendarSyncerConfig

import httplib2
httplib2.debuglevel=4

def main():
  conf = _loadConf('d/conf.pb')

  syncer = CalendarSyncer(conf)
  syncer.authenticate()
  syncer.syncEvents('d/kaggle.sqlite')

class CalendarSyncer(object):
  def __init__(self, conf):
    self.conf = conf
    self._service = None

  def authenticate(self):
    conf = self.conf

    with open(conf.authentication.serviceAccount.keysFile, 'rb') as f:
      key = f.read()

    http = httplib2.Http()

    credentials = SignedJwtAssertionCredentials(
      conf.authentication.serviceAccount.email,
      key,
      scope='https://www.googleapis.com/auth/calendar',
      sub=conf.target.email)
    credentials.refresh(http)
    http = credentials.authorize(http)

    self._service = build(
      serviceName='calendar', version='v3', http=http,
      developerKey=conf.authentication.developersKey)

  def syncEvents(self, sqliteFile):
    with sqlite3.connect(sqliteFile) as cn:
      rows = cn.execute('select id, blob from competitions')
      for id, blob in rows:
        c = Competition()
        c.ParseFromString(blob)

        self._syncCompetition(c)

  def _syncCompetition(self, competition):
    calendarId = self.conf.target.calendarId

    eventId = _eventId(competition)
    try:
      event = self._service.events().get(calendarId=calendarId, eventId=eventId).execute()
      if _match(competition, event):
        print '  [%s] no upate' % (competition.id)
      else:
        print '  [%s] update' % (competition.id)
        self._updateEvent(competition)
    except HttpError, e:
      if e.resp.status == 404:
        print '  [%s] insert' % (competition.id)
        self._addEvent(competition)
      else:
        raise e

  def _addEvent(self, competition):
    event = _event(competition)
    ev = self._service.events().insert(calendarId=self.conf.target.calendarId, body=event).execute()

  def _updateEvent(self, competition):
    event = _event(competition)
    ev = self._service.events().update(calendarId=self.conf.target.calendarId, eventId=event['id'], body=event).execute()

def _match(competition, event):
  return _event(competition) == event

def _event(competition):
  event = {
    'id': _eventId(competition),
    'summary': competition.title,
    'start': _jsonTime(competition.start),
    'end': _jsonTime(competition.end),
    'source': {
      'title': competition.title,
      'url': competition.url,
    },
  }
  return event

def _eventId(competition):
  return base64.b16encode(competition.id).lower()

def _jsonTime(dt):
  return {
      # '2011-06-03T10:25:00.000-07:00'
      'dateTime': time.strftime('%Y-%m-%dT%H:%M:%S.000-00:00', time.gmtime(dt.timestamp_utc))
  }

def _loadConf(confFile):
  with open(confFile) as f:
    s = f.read()

    conf = CalendarSyncerConfig()
    text_format.Merge(s, conf)

    return conf

if __name__ == '__main__':
  main()
