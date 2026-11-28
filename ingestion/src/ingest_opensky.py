import os
import sys
import json
import requests
import duckdb
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from warehouse import db_connection, RAW_DIR, DB_DEV_PATH

STATES_OPENSKY_DIR = RAW_DIR / 'states_opensky'
SCHEMA = 'raw'
TABLE = 'states_opensky'

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

    snapshot = datetime.fromtimestamp(data.get('time'), tz=timezone.utc)

    STATES_OPENSKY_DIR.mkdir(parents=True, exist_ok=True)

    path = STATES_OPENSKY_DIR / f'states_{snapshot:%Y%m%dT%H%M%S}.json'
    path.write_text(json.dumps(data))
    return path

def load_to_duckdb(path):

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f'File not found at {path}')

    with db_connection() as conn:
        conn.execute(f'create schema if not exists {SCHEMA}')

        conn.execute(
            f"""
            create table if not exists {SCHEMA}.{TABLE} (
                snapshot_time     bigint
                , states          json
                , source_file     varchar
                , loaded_on       timestamptz
            )
            """
        )

        before = conn.execute(
            f'select count(*) from {SCHEMA}.{TABLE} where source_file = ?'
            , [path.name]
        ).fetchone()[0]

        loaded_on = datetime.now(timezone.utc)

        try:
            conn.execute(
                f"""
                insert into {SCHEMA}.{TABLE}
                select
                    f.time              as snapshot_time
                    , s.state
                    , ?::varchar        as source_file
                    , ?::timestamptz    as loaded_on
                from read_json(
                    ?
                    , columns = {{time:'BIGINT', states:'JSON'}}
                ) f
                cross join lateral (
                    select unnest(from_json(f.states, '["JSON"]')) as state
                ) as s
                where not exists (
                    select 1
                    from {SCHEMA}.{TABLE} n
                    where
                        n.source_file = ?
                )
                """
                , [path.name, loaded_on, path.as_posix(), path.name]
            )

        except duckdb.Error as e:
            print(f'Failed to load {path.name}: {e}')
            return None

        after = conn.execute(
            f'select count(*) from {SCHEMA}.{TABLE} where source_file = ?'
            , [path.name]
        ).fetchone()[0]

        return after - before

if __name__ == '__main__':

    start = datetime.now(timezone.utc)
    print(f'States OpenSky ingestion started at {start:%Y-%m-%d %H:%M:%S} UTC')

    print('Requesting states API...')
    try:
        data = get_states()
    except requests.RequestException as e:
        print(f'Request failed: {e}')
        sys.exit(1)

    request_done = datetime.now(timezone.utc)
    print(f'Response returned in {(request_done - start).total_seconds():.1f} seconds')

    if data.get('time') is None:
        print('Response has no snapshot time, skipped storing and loading')
        sys.exit(1)

    path = store_data(data=data)
    count = len(data.get('states') or [])
    print(f'Stored {count} aircraft states in {path}')

    if count == 0:
        print(f'No aircraft states returned, skipped loading {path.name}')
    else:
        print(f'Inserting {path.name} snapshot into {DB_DEV_PATH.stem} warehouse at {SCHEMA} schema and {TABLE} table')
        inserted = load_to_duckdb(path=path)
        load_seconds = (datetime.now(timezone.utc) - request_done).total_seconds()

        if inserted is None:
            print(f'Load failed after {load_seconds:.1f} seconds')
            sys.exit(1)
        elif inserted == 0:
            print(f'Skipped {path.name}, already loaded')
        else:
            print(f'Inserted {inserted} rows in {load_seconds:.1f} seconds')

    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    print(f'Done in {elapsed:.1f} seconds')