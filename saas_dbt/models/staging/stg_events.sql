{{ config(
    materialized='incremental',
    unique_key=['user_id','event_date','event_type'],
    partition_by={
        "field": "event_date",
        "data_type": "date"
    },
    cluster_by=["user_id", "event_type"]
) }}

WITH source AS (

    SELECT
        user_id,
        event_type,
        DATE(timestamp) AS event_date
    FROM {{ source('raw', 'events_raw') }}

)

SELECT
    user_id,

    CASE
        WHEN event_type = 'signup' THEN 'signup'
        WHEN event_type = 'create_project' THEN 'create_project'
        ELSE 'other'
    END AS event_type,

    event_date

FROM source

{% if is_incremental() %}

WHERE event_date >= (
    SELECT DATE_SUB(MAX(event_date), INTERVAL 2 DAY)
    FROM {{ this }}
)

{% endif %}