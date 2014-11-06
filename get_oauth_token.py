from functools import partial
from lib import cmd
from lib.cmd import Command
from requests_oauthlib import OAuth2Session
import logging
import os

logger = logging.getLogger(__name__)

def login(command, args, conf):
  os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = "true"

  clientId = conf.auth.client_id
  clientSecret = conf.auth.client_secret
  redirectUri = conf.auth.redirect_uri

  authorizationBaseUrl = "https://accounts.google.com/o/oauth2/auth"
  tokenUrl = "https://accounts.google.com/o/oauth2/token"

  scope = [
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/calendar',
  ]

  google = OAuth2Session(clientId, scope=scope, redirect_uri=redirectUri)

  authorizationUrl, state = google.authorization_url(
    authorizationBaseUrl,
    access_type="offline",  # offline for refresh token
    approval_prompt="force" # force to always make user click authorize
  )
  print 'Please go here and authorize, %s' % authorizationUrl

  redirectResponse = raw_input('Paste the full redirect URL here:')

  token = google.fetch_token(
    tokenUrl,
    client_secret=clientSecret,
    authorization_response=redirectResponse)

  # Get refresh token
  refreshToken = token['refresh_token']
  print 'refresh_token=%s' % refreshToken

def refresh(command, args, conf):
  os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = "true"

  clientId = conf.auth.client_id
  clientSecret = conf.auth.client_secret
  redirectUri = conf.auth.redirect_uri
  refreshToken = conf.auth.refresh_token

  authorizationBaseUrl = "https://accounts.google.com/o/oauth2/auth"
  tokenUrl = "https://accounts.google.com/o/oauth2/token"

  scope = [
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/calendar',
  ]

  google = OAuth2Session(clientId, scope=scope, redirect_uri=redirectUri)
  token = google.refresh_token(tokenUrl,
    refresh_token=refreshToken,
    client_id=clientId,
    client_secret=clientSecret)

  accessToken = token['access_token']

  print 'access_token=%s' % accessToken

commands = {
  'login': partial(Command, login),
  'refresh': partial(Command, refresh)
}

if __name__ == '__main__':
  cmd.main(commands)
