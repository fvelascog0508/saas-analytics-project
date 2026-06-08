
{{ config(
    materialized='table',
    partition_by={
        "field": "event_date",
        "data_type": "date"
    },
    cluster_by=["user_id", "event_type"]
) }}


SELECT
    user_id,
    CASE
        WHEN event_type = 'signup' THEN 'signup'
        WHEN event_type = 'create_project' THEN 'create_project'
        ELSE 'other'
    END AS event_type,
    DATE(timestamp) AS event_date
FROM {{ source('raw', 'events_raw') }}

