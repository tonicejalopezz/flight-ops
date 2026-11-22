with master as (
    select *
    from {{ ref('stg_faa__master') }}
)

, aircraft as (
    select * 
    from {{ ref('stg_faa__aircraft_model') }}
)

, engine as (
    select *
    from {{ ref('stg_faa__engine_model') }}
)

, enrich as (
    select
        m.registration
        , m.serial_number
        , m.icao24
        , m.registrant_name
        , m.status_code
        , m.year_manufactured

        , a.model_name
        , a.manufacturer_name
        , m.aircraft_type_code
        , a.landing_surface_code
        , a.weight_class
        , a.seat_count
        , a.engine_count
        
        , e.engine_model_name
        , e.engine_manufacturer_name
        , e.engine_type_code
        , e.engine_thrust_lbs
        , e.engine_horsepower

        , m.cert_issue_date
        , m.registration_expires_on
    
    from master m

    left join aircraft a 
        on m.model_code = a.model_code

    left join engine e
        on m.engine_code = e.engine_code
)

select *
from enrich