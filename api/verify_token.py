import requests
import json

def verify_token(token:str, api_id:int) -> tuple:
    '''
    Do token verification. 
    Params:
        token       :(int) token to be verified
        api_id      :(str) API ID, it should be the same as the id in MySQL database. Contact token admin if you dont know your api id 

        
    Returns:
        isVerified  :(bool) illegal or not
        message     :(str) system message
    '''
    
    response = requests.post('http://140.116.245.157:3001/token_verification', {'token': token, "api_id":api_id}) # Make sure your service_id is correct!

    if response.status_code == 200:
        res = json.loads(response.text)
        if res['status']:
            return True, res["msg"]
        else:
            return False, res["msg"]
    else: # Can't connect to token-system. Check if the server is running.
        return False, "Server mantainese"
