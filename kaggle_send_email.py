from data_pb2 import Competition, Date, CalendarSyncerConfig
from email.mime.text import MIMEText
from functools import partial
from itertools import islice
from lib import cmd
from lib.cmd import Command
from lib.files import readFile
from oauth2client.client import SignedJwtAssertionCredentials
import apiclient
import base64
import calendar
import httplib2
import logging
import sqlite3
import time
from oauth import oauthSession

logger = logging.getLogger(__name__)

def email(command, args, conf):
  sqliteStorage = SqliteStorage(conf.sqliteSyncer.sqliteFile)
  lastTs = sqliteStorage.lastLog(category='email')
  if lastTs is None:
    lastTs = calendar.timegm(time.gmtime())
    sqliteStorage.log(category='email', value=_timestampToString(lastTs))
  else:
    lastTs = _timestampFromString(lastTs)

  competitions = list(sqliteStorage.competitions(startedAfter=lastTs))
  if len(competitions) <= 0:
    logger.info('email, sent=0')
    return

  sender = EmailSender(conf)

  emails = 0
  for c in competitions:
    sender.email(c)
    emails += 1

    # sqliteStorage.log(category='email', value=_timestampToString(c.start.timestampUtc))

  logger.info('email, sent=%d' % (emails))

class EmailSender(object):
  def __init__(self, conf):
    self.conf = conf

    scope = [
      'https://www.googleapis.com/auth/gmail.compose',
    ]
    self.google = oauthSession(conf, scope)

  def email(self, competition):
    _message(competition)
    headers = {'Content-Type':  'application/json'}
    self.google.post(
      'https://www.googleapis.com/gmail/v1/users/me/messages/send',
      data={'raw': _message(competition)},
      params={'uploadType': 'media'},
      headers=headers,
    )

def _message(competition):
  message = MIMEText(competition.description)
  message['to'] = 'deemonster@gmail.com'
  message['from'] = 'kaggle-calendar@gmail.com'
  message['subject'] = competition.title
  return base64.urlsafe_b64encode(message.as_string())

class SqliteStorage():
  def __init__(self, sqliteFile):
    self.sqliteFile = sqliteFile

  def competitions(self, startedAfter=None):
    competitionF = None
    if not startedAfter is None:
      competitionF = lambda competition: startedAfter < competition.start.timestampUtc

    if competitionF is None:
      competitionF = lambda competition: True

    with sqlite3.connect(self.sqliteFile) as cn:
      rows = cn.execute('select id, blob from competitions')
      for id, blob in rows:
        c = Competition()
        c.ParseFromString(blob)

        if competitionF(c):
          yield c

  def lastLog(self, category=None):
    where = []
    whereArgs = dict()

    if category:
      where.append('category=:category')
      whereArgs['category'] = category

    with sqlite3.connect(self.sqliteFile) as cn:
      sql = 'select value from log'
      if 0 < len(where):
        sql = '%s where %s' % (sql, ' and '.join(where))
      sql = sql + ' order by ts desc limit 1'
      rows = list(islice(cn.execute(sql, whereArgs), 1))
      if len(rows) <= 0:
        return None

      return rows[0][0]

  def log(self, category=None, value=None):
    with sqlite3.connect(self.sqliteFile) as cn:
      cn.execute(
          "insert into log (ts, category, value) values (datetime('now'), :category, :value)",
          { 'category': category, 'value': value })

def _timestampFromString(s):
  return calendar.timegm(time.strptime(s, '%Y-%m-%dT%H:%M:%S.000-00:00'))

def _timestampToString(ts):
  return time.strftime('%Y-%m-%dT%H:%M:%S.000-00:00', time.gmtime(ts))

commands = {
  'email': partial(Command, email),
}

if __name__ == '__main__':
  cmd.main(commands)
