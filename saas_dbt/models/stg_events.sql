SELECT
    user_id,
    event_type,
    timestamp,
    DATE(timestamp) AS event_date
FROM {{ source('raw', 'events_raw') }}
