 with source as (
    select 
        *
    from {{ source('faa', 'acftref') }}
 )

, cleanse_source as (
    select
        nullif(trim(code), '')           as model_code
        , nullif(trim(model), '')            as model_name
        
        , nullif(trim(mfr), '')            as manufacturer_name
        , nullif(trim(acweight), '')       as weight_class

        , try_cast(nullif(trim(noseats), '') as integer)     as seat_count
        , try_cast(nullif(trim(noeng), '') as integer)       as engine_count
        , try_cast(nullif(trim(speed), '') as integer)       as cruising_speed_mph
        , nullif(trim(accat), '')                            as landing_surface_code
        , nullif(trim(buildcertind), '')                     as builder_certification_code

        , nullif(trim(tcdatasheet), '')    as type_certificate_data_sheet
        , nullif(trim(tcdataholder), '')   as type_certificate_data_holder

        , source_file
        , loaded_on

    from source
)

select * 
from cleanse_source