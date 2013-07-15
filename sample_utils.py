#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for Analytics API code samples.

Handles various tasks to do with logging, authentication and initialization.
Mostly taken from Sergio :)

Before You Begin:

You must update the client_secrets.json file with a client id, client secret,
and the redirect uri. You get these values by creating a new project
in the Google APIs console and registering for OAuth2.0 for installed
applications: https://code.google.com/apis/console

Also all OAuth2.0 tokens are stored for resue in the file specified
as TOKEN_FILE_NAME. You can modify this file name if you wish.
"""

__author__ = ('sergio.gomes@google.com (Sergio Gomes)'
              'api.nickm@gmail.com (Nick Mihailovski)')

import logging
import os
import sys
from apiclient.discovery import build
import gflags
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OOB_CALLBACK_URN
from oauth2client.file import Storage
from oauth2client.tools import run

import collections
import urllib,urllib2,httplib2,json

FLAGS = gflags.FLAGS

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You get these values by
# creating a new project in the Google APIs console and registering for
# OAuth2.0 for installed applications: <https://code.google.com/apis/console>
CLIENT_SECRETS = 'client_secrets.json'


# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console <https://code.google.com/apis/console>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)

setdir=os.path.abspath('.')
file=setdir+'\\client_secrets.json'

# Set up a Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(file,scope='https://www.googleapis.com/auth/analytics.readonly',redirect_uri=OOB_CALLBACK_URN)

# The gflags module makes defining command-line options easy for applications.
# Run this program with the '--help' argument to see all the flags that it
# understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
                   ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                   'Set the level of logging detail.')


# Name of file that will store the access and refresh tokens to access
# the API without having to login each time. Make sure this file is in
# a secure place.
TOKEN_FILE_NAME = setdir+'\\analytics.dat'


def process_flags(argv):
  """Uses the command-line flags to set the logging level.

  Args:
    argv: List of command line arguments passed to the python script.
  """

  # Let the gflags module process the command-line arguments.
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\nUsage: %s ARGS\n%s' % (e, argv[0], FLAGS)
#    sys.exit(1)

  # Set the logging according to the command-line flag.
  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))


def initialize_service(proxySetting={'proxy':'http'}):
  """Returns an instance of service from discovery data and does auth.

  This method tries to read any existing OAuth 2.0 credentials from the
  Storage object. If the credentials do not exist, new credentials are
  obtained. The crdentials are used to authorize an http object. The
  http object is used to build the analytics service object.

  Returns:
    An analytics v3 service object.
  """

  # Create an httplib2.Http object to handle our HTTP requests.
  
  #Create proxy using socks V5
  
  http=None
  if proxySetting['proxy']=='Socks':
    if proxySetting['proxyIP']!='' and proxySetting['proxyPort']!='':
      proxy=httplib2.ProxyInfo(2, proxySetting['proxyIP'], int(proxySetting['proxyPort']))
      proxyUrl=proxySetting['proxyIP']+':'+proxySetting['proxyPort']
      proxy0=urllib2.ProxyHandler({'https':proxyUrl})
      opener=urllib2.build_opener(proxy0)
      urllib2.install_opener(opener)
      http = httplib2.Http(proxy_info = proxy,disable_ssl_certificate_validation=True)# set proxy  close  SSL
    else:
      http = httplib2.Http()  
  else:
    http = httplib2.Http()
    print 'no socks'

  # Prepare credentials, and authorize HTTP object with them.
  storage = Storage(TOKEN_FILE_NAME)
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  http = credentials.authorize(http)

  # Retrieve service.
  return build('analytics', 'v3', http=http)
  
  
  
def main(argv):
  process_flags(argv)

  # Authenticate and construct service.
  service = initialize_service()

  # Try to make a request to the API. Print the results or handle errors.
           
if __name__ == '__main__':
  main(sys.argv)