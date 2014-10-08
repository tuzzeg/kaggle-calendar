from apiclient.discovery import build
from apiclient.errors import HttpError
from data_pb2 import Competition, Date, CalendarSyncerConfig
from functools import partial
from lib import cmd
from lib.cmd import Command
from lib.files import readFile
from oauth2client.client import SignedJwtAssertionCredentials
import base64
import httplib2
import logging
import sqlite3
import time

logger = logging.getLogger(__name__)

def _sync(conf):
  syncer = CalendarSyncer(conf)
  syncer.authenticate()
  syncer.syncEvents(conf.sqliteSyncer.sqliteFile)

class CalendarSyncer(object):
  def __init__(self, conf):
    self.conf = conf.calendarSyncer
    self._service = None

  def authenticate(self):
    conf = self.conf.authentication

    http = httplib2.Http()

    credentials = SignedJwtAssertionCredentials(
      conf.serviceAccount.email,
      readFile(conf.serviceAccount.keysFile),
      scope='https://www.googleapis.com/auth/calendar')
    http = credentials.authorize(http)

    self._service = build(
      serviceName='calendar', version='v3', http=http,
      developerKey=conf.developersKey)

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
        logger.debug('[%s] no upate' % (competition.id))
      else:
        logger.debug('[%s] update' % (competition.id))
        self._updateEvent(competition)
    except HttpError, e:
      if e.resp.status == 404:
        logger.debug('[%s] insert' % (competition.id))
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
    'description': competition.description,
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
      'dateTime': time.strftime('%Y-%m-%dT%H:%M:%S.000-00:00', time.gmtime(dt.timestampUtc))
  }

def sync(command, args, conf):
  _sync(conf)

commands = {
  'sync': partial(Command, sync)
}

if __name__ == '__main__':
  cmd.main(commands)
