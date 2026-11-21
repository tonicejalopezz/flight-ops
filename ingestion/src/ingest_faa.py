import io
import duckdb
import zipfile
import requests
from datetime import datetime, timezone
from warehouse import db_connection, RAW_DIR, DB_DEV_PATH

FAA_DIR = RAW_DIR / 'faa_releasable_aircraft'
SCHEMA = 'raw'

REQUEST_TIMEOUT = 30

REQ_FILES = {
    'MASTER.txt'
    , 'ENGINE.txt'
    , 'ACFTREF.txt'
}

def download_zip():
    response = requests.get(
        'https://registry.faa.gov/database/ReleasableAircraft.zip'
        , headers={'User-Agent': 'Mozilla/5.0'}
        , timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    FAA_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(path=FAA_DIR)

def load_to_duckdb():

    with db_connection() as conn:
        conn.execute(f'create schema if not exists {SCHEMA}')
        loaded_on = datetime.now(timezone.utc)

        for name in sorted(REQ_FILES):

            file = FAA_DIR / name
            table = f'faa_{file.stem.lower()}'
            path = file.as_posix()

            try:
                conn.execute(
                    f"""
                    create or replace table {SCHEMA}.{table} as
                    select
                        *
                        , ?::varchar      as source_file
                        , ?::timestamptz  as loaded_on
                    from read_csv(
                        '{path}'
                        , header = true
                        , all_varchar = true
                        , normalize_names = true
                    )
                    """
                    , [file.name, loaded_on]
                )

                count = conn.execute(f'select count(*) from {SCHEMA}.{table}').fetchone()[0]
                print(f'Loaded {count} rows into {SCHEMA}.{table}')

            except duckdb.Error as e:
                print(f'Failed to load {file.name}: {e}')


if __name__ == '__main__':
    
    start = datetime.now(timezone.utc)
    print(f'FAA aircraft ingestion started at {start:%Y-%m-%d %H:%M:%S} UTC')

    print('Downloading ReleasableAircraft.zip...')
    download_zip()
    print(f'Extracted to {FAA_DIR}')

    print(f'Loading files into {DB_DEV_PATH.stem} warehouse in {SCHEMA} schema')
    load_to_duckdb()

    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    print(f'Done in {elapsed:.1f} seconds')