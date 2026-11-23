{{
    config(materialized='table')
}}

with aircraft_enrich as (
    select * 
    from {{ ref('int_faa__aircraft_enrich') }}
)

, decoded as (
    select 
        a.*
        , w.description             as weight_class_desc
        , s.description             as status_desc
        , l.description             as landing_surface_desc
        , e.description             as engine_desc
        , ac.description            as aircraft_desc

    from aircraft_enrich a

    left join {{ ref('faa_weight_class') }} w
        on a.weight_class = w.weight_class

    left join {{ ref('faa_status_code') }} s
        on a.status_code = s.status_code

    left join {{ ref('faa_landing_surface_type') }} l
        on a.landing_surface_code = l.landing_surface_code

    left join  {{ ref('faa_engine_type') }} e
        on a.engine_type_code = e.engine_type_code

    left join {{ ref('faa_aircraft_type') }} ac
        on a.aircraft_type_code = ac.aircraft_type_code
)

, final as (
    select
        -- identifiers
        sha256(icao24)                      as aircraft_key
        , icao24
        , registration
        , serial_number

        -- registrant
        , registrant_name

        -- aircraft attributes
        , manufacturer_name
        , model_name
        , aircraft_desc
        , weight_class_desc
        , seat_count
        , landing_surface_desc
        , year_manufactured

        -- engine attributes
        , engine_count
        , engine_manufacturer_name
        , engine_model_name
        , engine_desc
        , engine_thrust_lbs
        , engine_horsepower

        -- registration
        , status_desc
        , cert_issue_date
        , registration_expires_on

    from decoded

)

select *
from final