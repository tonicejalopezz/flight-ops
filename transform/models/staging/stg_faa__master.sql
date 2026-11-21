with source as (
    select *
    from {{ source('faa', 'faa_master') }}
)

, cleanse_source as (
    select
        lower(nullif(trim(mode_s_code_hex), ''))      as icao24
        , 'N' || trim(nnumber)                        as registration
        , nullif(trim(serial_number), '')             as serial_number
        , nullif(trim(unique_id), '')                 as faa_unique_id

        , nullif(trim(_name), '')                     as registrant_name
        , nullif(trim(street), '')                    as registrant_street
        , nullif(trim(street2), '')                   as registrant_street_line_2
        , nullif(trim(city), '')                      as registrant_city
        , nullif(trim(state), '')                     as registrant_state
        , nullif(trim(zip_code), '')                  as registrant_zip_code
        , nullif(trim(country), '')                   as registrant_country
        , nullif(trim(type_registrant), '')            as type_registrant

        , nullif(trim(mfr_mdl_code), '')                          as model_code
        , nullif(trim(eng_mfr_mdl), '')                           as engine_code
        , try_cast(nullif(trim(year_mfr), '') as integer)         as year_manufactured
        , nullif(trim(type_aircraft), '')                         as aircraft_type_code
        , nullif(trim(type_engine), '')                           as engine_type_code
        , nullif(trim(status_code), '')                           as status_code

        , try_strptime(nullif(trim(cert_issue_date), ''), '%Y%m%d')::date   as cert_issue_date
        , try_strptime(nullif(trim(air_worth_date), ''), '%Y%m%d')::date    as airworthiness_date
        , try_strptime(nullif(trim(expiration_date), ''), '%Y%m%d')::date   as registration_expires_on
        , try_strptime(nullif(trim(last_action_date), ''), '%Y%m%d')::date  as last_action_date

        , source_file
        , loaded_on

    from source
)

select *
from cleanse_source