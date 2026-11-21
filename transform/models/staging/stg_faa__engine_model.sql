with source as (
    select *
    from {{ source('faa', 'engine') }}
)

, cleanse_source as (
    select 
        nullif(trim(code), '')      as engine_code
        , nullif(trim(model), '')   as engine_model_name

        , nullif(trim(mfr), '')     as engine_manufacturer_name        
        , nullif(trim(_type), '')   as engine_type_code

        , try_cast(nullif(trim(horsepower), '') as integer) as engine_horsepower
        , try_cast(nullif(trim(thrust), '') as integer) as engine_thrust_lbs

        , source_file
        , loaded_on

    from source 
)

select * 
from cleanse_source