{{ config(
    materialized='table',
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
GROUP BY event_date, event_type