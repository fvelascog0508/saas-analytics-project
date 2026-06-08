SELECT
    event_date,
    COUNT(DISTINCT user_id) AS active_users
FROM {{ ref('stg_events') }}
GROUP BY event_date
ORDER BY event_date