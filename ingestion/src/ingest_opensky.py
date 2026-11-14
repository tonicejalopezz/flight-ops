import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw' 

load_dotenv()

TOKEN_URL = 'https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token'

TOKEN_MARGIN_REFRESH = 30
REQUEST_TIMEOUT = 30

class TokenManager: 
    def __init__(self):
        self.token = None
        self.expires_at = None

    def refresh_token(self):

        response = requests.post(
            TOKEN_URL
            , data = {
                'grant_type' : 'client_credentials'
                , 'client_id' : os.environ['OPENSKY_CLIENT_ID']
                , 'client_secret': os.environ['OPENSKY_CLIENT_SECRET']
            }
            , timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()
        self.token = data['access_token']
        expires_in = data.get('expires_in', 1800)

        self.expires_at = datetime.now() + timedelta(seconds=expires_in - TOKEN_MARGIN_REFRESH)

        return self.token

    def get_token(self):
        
        if self.token and self.expires_at and datetime.now() < self.expires_at: 
            return self.token
        
        return self.refresh_token()

    def headers(self):
        return {'Authorization' : f'Bearer {self.get_token()}'}

tokens = TokenManager()

def get_states():

    response = requests.get(
        'https://opensky-network.org/api/states/all'
        , headers=tokens.headers()
        , timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()
    
    return response.json()

def store_data(data):

    snapshot = datetime.fromtimestamp(data.get('time'))

    folder = RAW_DIR / 'states_opensky'
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f'states_{snapshot:%Y%m%dT%H%M%S}.json'
    path.write_text(json.dumps(data))
    return path

if __name__ == '__main__':

    data = get_states()
    path = store_data(data=data)

    count = len(data.get('states') or [])

    print(f'Saved {count} aircrafts to {path} at {datetime.now()}')