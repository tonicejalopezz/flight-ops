with source as (
    select
        *
    from {{ source('faa', 'faa_acftref') }}
)

, cleanse_source as (
    select
        nullif(trim(code), '')             as model_code
        , nullif(trim(model), '')          as model_name

        , nullif(trim(mfr), '')            as manufacturer_name
        , nullif(trim(acweight), '')       as weight_class

        , nullif(try_cast(nullif(trim(noseats), '') as integer), 0)     as seat_count
        , nullif(try_cast(nullif(trim(noeng), '') as integer), 0)       as engine_count
        , nullif(try_cast(nullif(trim(speed), '') as integer), 0)       as cruising_speed_mph
        , nullif(trim(accat), '')                                       as landing_surface_code
        , nullif(trim(buildcertind), '')                                as builder_certification_code

        , nullif(trim(tcdatasheet), '')    as type_certificate_data_sheet
        , nullif(trim(tcdataholder), '')   as type_certificate_data_holder

        , source_file
        , loaded_on at time zone 'UTC'     as loaded_on

    from source
)

select *
from cleanse_source