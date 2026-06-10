{{ config(
    materialized='incremental',
    partition_by={
        "field": "event_date",
        "data_type": "date"
    }
) }}

SELECT
    event_date,
    event_type,
    COUNT(DISTINCT user_id) AS users
FROM {{ ref('stg_events') }}

{% if is_incremental() %}

WHERE event_date >= (
    SELECT DATE_SUB(MAX(event_date), INTERVAL 2 DAY)
    FROM {{ this }}
)

{% endif %}

GROUP BY event_date, event_type
