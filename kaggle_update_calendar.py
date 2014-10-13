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

def _sync(conf, id=None):
  if id is None:
    competitionF = lambda competition: True
  else:
    competitionF = lambda competition: competition.id == id

  syncer = CalendarSyncer(conf)
  syncer.authenticate()
  syncer.syncEvents(conf.sqliteSyncer.sqliteFile, competitionF)

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

  def syncEvents(self, sqliteFile, competitionF):
    calendars = {
      _all: self.conf.targetAll.calendarId,
      _inMoney: self.conf.targetInMoney.calendarId,
      _knowledge: self.conf.targetKnowledge.calendarId,
    }

    with sqlite3.connect(sqliteFile) as cn:
      rows = cn.execute('select id, blob from competitions')
      for id, blob in rows:
        c = Competition()
        c.ParseFromString(blob)

        if competitionF(c):
          for predicate, calendarId in calendars.items():
            if predicate(c):
              self._syncCompetition(calendarId, c)

  def _syncCompetition(self, calendarId, competition):
    eventId = _eventId(competition)
    try:
      event = self._service.events().get(calendarId=calendarId, eventId=eventId).execute()
      if _match(competition, event):
        logger.debug('[%s] no upate' % (competition.id))
      else:
        logger.debug('[%s] update' % (competition.id))
        self._updateEvent(calendarId, competition)
    except HttpError, e:
      if e.resp.status == 404:
        logger.debug('[%s] insert' % (competition.id))
        self._addEvent(calendarId, competition)
      else:
        raise e

  def _addEvent(self, calendarId, competition):
    event = _event(competition)
    ev = self._service.events().insert(calendarId=calendarId, body=event).execute()

  def _updateEvent(self, calendarId, competition):
    event = _event(competition)
    ev = self._service.events().update(calendarId=calendarId, eventId=event['id'], body=event).execute()

def _match(competition, event):
  return _event(competition) == event

def _event(competition):
  event = {
    'id': _eventId(competition),
    'summary': competition.title,
    'description': '<a href="%s">%s</a>' % (competition.url, competition.description),
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

def _all(competition):
  return True

def _inMoney(competition):
  return competition.HasField('rewardUsd')

def _knowledge(competition):
  return Competition.KNOWLEDGE in competition.attributes

def syncAll(command, args, conf):
  _sync(conf)

class Sync(object):
  def argparser(self, p):
    p.add_argument('--event-id', type=str)

  def __call__(self, command, args, conf):
    _sync(conf, id=args.event_id)

commands = {
  'sync-all': partial(Command, syncAll),
  'sync': partial(Command, Sync())
}

if __name__ == '__main__':
  cmd.main(commands)
