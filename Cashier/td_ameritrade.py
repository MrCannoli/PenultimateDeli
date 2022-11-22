import requests 
import logging
from os import getenv
from dotenv import load_dotenv
from urllib.parse import unquote

# To get your own client_id (consumer key) you need to register an app here
# https://developer.tdameritrade.com/user/me/apps
# use http://127.0.0.1:8080 as the calback url

load_dotenv() # load environment variables from .env file
redirect_uri = getenv('REDIRECT_URI')
client_id = getenv('CLIENT_ID') + '@AMER.OAUTHAP' # this is required to be added after your client_id string. It's not documented why.
post_access_token_code = getenv('POST_ACCESS_TOKEN_CODE')
log_file = getenv('LOG_FILE')
undecoded_token = getenv('UNDECODED_TOKEN')

logging.basicConfig(filename=log_file, level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
logging.info("\n\n================================================\nStarting new run: \n\n")

'''
Main AUTH function which will return a token. Assuming the status is a success, you can use the URL to connect to the app. 
See https://developer.tdameritrade.com/content/simple-auth-local-apps for more details
example request URL:
https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2F127.0.0.1:8080&client_id=EXAMPLE%40AMER.OAUTHAP
'''
def request_auth_token():
    response_type = 'code' # there seem to be other response types here but are undocumented
    auth_url = 'https://auth.tdameritrade.com/auth' 
    logging.info(f'Running AUTH: {auth_url}')

    req_response = requests.get(auth_url , params={ 'response_type': response_type, 'redirect_uri': redirect_uri, 'client_id': client_id})
    logging.info(req_response.text)
    logging.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    logging.info(req_response.url)
    logging.info(req_response.status_code) # 200 == success
    #print(req_response.json())

'''
URL decode a given URL
'''
def url_decode():
    logging.info("Decoded URL: " + unquote(undecoded_token))

'''
Request a POST access token. This token is required to give the app access to trading and other functionality.
'''
def request_post_access_token():
    req_url = "https://api.tdameritrade.com/v1/oauth2/token"
    grant_type = "authorization_code"
    #grant_type = "refresh_code"
    access_type = "offline"
    headers = {'Allow':'GET, POST'}

    # req_response = requests.get(req_url , params={ 'grant_type': grant_type, 'access_type': access_type, 'code': post_access_token_code, 
    #                             'headers': "Allow: GET, POST", 'redirect_uri': redirect_uri, 'client_id': client_id + post_client_id},  
    #                             headers=headers)
    
    req_response = requests.post(req_url , params={ 'grant_type': grant_type, 'access_type': access_type, 'code': post_access_token_code, 
                                 'redirect_uri': redirect_uri, 'client_id': client_id}, headers=headers)

    logging.info(req_response.text)
    logging.info(req_response.url)
    logging.info(req_response.status_code) # 200 == success

    

'''
TODO:
- Get post access token to work
    - Look into requests: https://requests.readthedocs.io/en/latest/
    - https://stackoverflow.com/questions/23276728/405-status-code-not-returning-the-response-properly
    - https://datagy.io/python-requests-headers/
- Get a quote request for google to work
- Create class for TD Ameritrade
    - Request for individual stocks quotes
    - Request stock history
    - Make buy order
    - Make sell order
      - Use Sell Trailing Stop for low limit? May be problematic if I can't get feedback on sales.
'''

