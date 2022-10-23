import requests 
import LocalKeys.keys #import Keys # Repo with keys for dev u se

# To get your own client_id (consumer key) you need to register an app here
# https://developer.tdameritrade.com/user/me/apps
# use http://127.0.0.1:8080 as the calback url

redirect_uri = 'http://127.0.0.1:8080' # localhost for simplicity
client_id = LocalKeys.keys.app_consumer_key
print(client_id)
#post_client_id = '@AMER.OAUTHAP' # this is required to be added after your client_id string. no idea why. lol
post_client_id = "%40AMER.OAUTHAP"
response_type = 'code' # there seem to be other response types here but are undocumented
auth_url = 'https://auth.tdameritrade.com/auth' 
req_url = 'https://api.tdameritrade.com/v1/marketdata/GOOG/quotes'

#'https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2F127.0.0.1:8080&client_id=EXAMPLE%40AMER.OAUTHAP'
req_response = requests.get(auth_url , params={ 'response_type': response_type, 'redirect_uri': redirect_uri, 'client_id': client_id + post_client_id})

print(req_response.text)
print(req_response.url)
print(req_response.status_code)
#print(req_response.json())

