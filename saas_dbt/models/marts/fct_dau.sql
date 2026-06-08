{{ config(
    materialized='table',
    partition_by={
        "field": "event_date",
        "data_type": "date"
    }
) }}

SELECT
    event_date,
    COUNT(DISTINCT user_id) AS active_users
FROM {{ ref('stg_events') }}
GROUP BY event_date