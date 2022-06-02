import requests 

# To get your own client_id (consumer key) you need to register an app here
# https://developer.tdameritrade.com/user/me/apps
# use http://127.0.0.1:8080 as the calback url

redirect_uri = 'http://127.0.0.1:8080'
client_id = 'SLA5LLBCWLLMDG8CBZTGBYVLPAWNTPLK'
post_client_id = '@AMER.OAUTHAP' # this is required to be added after your client_id string. no idea why. lol
response_type = 'code' # there seem to be other response types here but are undocumented
auth_url = 'https://auth.tdameritrade.com/auth' 

#'https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2F127.0.0.1:8080&client_id=EXAMPLE%40AMER.OAUTHAP'
# https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080&client_id=SLA5LLBCWLLMDG8CBZTGBYVLPAWNTPLK
auth_response = requests.get(auth_url , params={ 'response_type': response_type, 'redirect_uri': redirect_uri, 'client_id': client_id + post_client_id })
print(auth_response.text)
print(auth_response.url)


