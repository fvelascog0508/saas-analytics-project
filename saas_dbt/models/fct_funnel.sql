SELECT
    event_type,
    COUNT(DISTINCT user_id) AS users
FROM {{ ref('stg_events') }}
GROUP BY event_type
ORDER BY users DESC
