from cStringIO import StringIO
import sqlite3

moz_cookies_file = '/Users/sd/Library/Application Support/Firefox/Profiles/s3wv9v6i.default/cookies.sqlite'

def loadMain():
  import os, cookielib, urllib2
  cj = cookielib.MozillaCookieJar()
  cj.load(os.path.join(os.path.expanduser("~"), ".netscape", "cookies.txt"))
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  r = opener.open("http://kaggle.com")

def loadCookieJar(file):
  cn = sqlite3.connect(moz_cookies_file)

  c = cn.cursor()
  c.execute("select host, path, isSecure, expiry, name, value from moz_cookies where baseDomain==?", ("kaggle.com",))

  ftstr = ["FALSE","TRUE"]
  s = StringIO()
  s.write("""\
  # Netscape HTTP Cookie File
  # http://www.netscape.com/newsref/std/cookie_spec.html
  # This is a generated file!  Do not edit.
  """)
  for item in c.fetchall():
      s.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
          item[0],
          ftstr[item[0].startswith('.')],
          item[1],
          ftstr[item[2]],
          item[3],
          item[4],
          item[5]))

  s.seek(0)

  cookie_jar = cookielib.MozillaCookieJar()
  cookie_jar._really_load(s, '', True, True)
  return cookie_jar
