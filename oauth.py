import os
from requests_oauthlib import OAuth2Session

def oauthSession(conf, scope):
  os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = "true"

  authorizationBaseUrl = "https://accounts.google.com/o/oauth2/auth"
  tokenUrl = "https://accounts.google.com/o/oauth2/token"

  google = OAuth2Session(
    conf.auth.client_id,
    scope=scope,
    redirect_uri=conf.auth.redirect_uri)
  google.refresh_token(
    tokenUrl,
    refresh_token=conf.auth.refresh_token,
    client_id=conf.auth.client_id,
    client_secret=conf.auth.client_secret)

  return google
