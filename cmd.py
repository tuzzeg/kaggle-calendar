from config import loadConfig
import argparse
import logging
import sys
import urllib2

class Command(object):
  def __init__(self, inner):
    self._inner = inner

  def argparser(self, p):
    p.add_argument('-c', '--configs', nargs='+')
    p.add_argument('--log-level', type=str, default='WARNING')
    p.add_argument('--log-http', type=bool, default=False)
    if hasattr(self._inner, 'argparser'):
      self._inner.argparser(p)

  def __call__(self, command, args):
    logLevel = getattr(logging, args.log_level.upper(), None)
    if not isinstance(logLevel, int):
      raise ValueError('Invalid log level: %s' % args.log_level)
    logging.basicConfig(level=logLevel)

    if args.log_http:
      http_logger = urllib2.HTTPHandler(debuglevel = 1)
      opener = urllib2.build_opener(http_logger) # put your other handlers here too!
      urllib2.install_opener(opener)

    conf = loadConfig(*args.configs)

    print self._inner
    self._inner(command, args, conf)

def main(commands):
  if len(sys.argv) < 2:
    print 'usage: %s cmd ...' % (sys.argv[0])
    sys.exit(-1)

  command = sys.argv[1]
  rawArgs = sys.argv[2:]

  cmdF = commands[command]
  if not cmdF:
    print 'Unknown command, expected one of [%s]' % (' '.join(commands))
  cmd = cmdF()

  p = argparse.ArgumentParser()
  cmd.argparser(p)
  args = p.parse_args(rawArgs)

  cmd(command, args)
