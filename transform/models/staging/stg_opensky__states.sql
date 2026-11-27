with source as (
    select *
    from {{ source('opensky', 'states_opensky') }}
)

, extract_and_cleanse_source as (
    select
        lower(nullif(trim(states->>'$[0]'), ''))                as icao24
        , nullif(trim(states->>'$[1]'), '')                     as callsign
        , nullif(trim(states->>'$[2]'), '')                     as origin_country

        , to_timestamp(
            try_cast(states->>'$[3]' as bigint)
        ) at time zone 'UTC'                                    as time_position
        , to_timestamp(
            try_cast(states->>'$[4]' as bigint)
        ) at time zone 'UTC'                                    as last_contact

        , try_cast(states->>'$[5]' as double)                   as longitude
        , try_cast(states->>'$[6]' as double)                   as latitude
        , try_cast(states->>'$[7]' as double)                   as baro_altitude
        , try_cast(states->>'$[8]' as boolean)                  as on_ground
        , try_cast(states->>'$[9]' as double)                   as velocity
        , try_cast(states->>'$[10]' as double)                  as true_track
        , try_cast(states->>'$[11]' as double)                  as vertical_rate
        , try_cast(states->>'$[13]' as double)                  as geo_altitude
        , nullif(trim(states->>'$[14]'), '')                    as squawk
        , try_cast(states->>'$[15]' as boolean)                 as spi
        , try_cast(states->>'$[16]' as integer)                 as position_sources

        , to_timestamp(snapshot_time) at time zone 'UTC'        as snapshot_time
        , source_file
        , loaded_on at time zone 'UTC'                          as loaded_on

    from source
)

select *
from extract_and_cleanse_source