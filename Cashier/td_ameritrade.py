# To get your own client_id (consumer key) you need to register an app here
# https://developer.tdameritrade.com/user/me/apps

import requests 
import os
import logging
from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env file
redirect_uri = os.getenv('REDIRECT_URI')
client_id = os.getenv('CLIENT_ID') + "%40AMER.OAUTHAP"  # this is required to be appended to your client_id string. no idea why. lol
response_type = 'code' # there seem to be other response types here but are undocumented
auth_url = os.getenv('AUTH_URL')
req_url = os.getenv('REQ_URL')

'''
Main AUTH function which will return a token 
example request URL:
https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2F127.0.0.1:8080&client_id=EXAMPLE%40AMER.OAUTHAP
'''
def auth():
  logging.info(f'Running AUTH: {auth_url}')
  req_response = requests.get(auth_url , params={ 'response_type': response_type, 'redirect_uri': redirect_uri, 'client_id': client_id})

  logging.info(req_response.text)
  logging.info(req_response.url)
  logging.info(req_response.status_code)
  #print(req_response.json())

'''
TODO:
- Figure out how to verify auth url works
- Get a quote request for google to work
- Create class for TD Ameritrade
  - Request for individual stocks quotes
  - Make buy order
  - Make sell order
'''

