with source as (
    select *
    from {{ source('faa', 'faa_engine') }}
)

, cleanse_source as (
    select 
        nullif(trim(code), '')      as engine_code
        , nullif(trim(model), '')   as engine_model_name

        , nullif(trim(mfr), '')     as engine_manufacturer_name        
        , nullif(trim(_type), '')   as engine_type_code

        , nullif(try_cast(nullif(trim(horsepower), '') as integer), 0)  as engine_horsepower
        , nullif(try_cast(nullif(trim(thrust), '') as integer), 0)      as engine_thrust_lbs

        , source_file
        , loaded_on

    from source 
)

select * 
from cleanse_source