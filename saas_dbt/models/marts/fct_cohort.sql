{{ config(
    materialized='table',
    partition_by={
        "field": "cohort_date",
        "data_type": "date"
    },
    cluster_by=["days_since_signup"]
) }}

WITH first_events AS (

    -- primer evento (define el cohort)
    SELECT
        user_id,
        MIN(event_date) AS cohort_date
    FROM {{ ref('stg_events') }}
    GROUP BY user_id

),

events_with_cohort AS (

    -- unir eventos con su cohort
    SELECT
        e.user_id,
        f.cohort_date,
        e.event_date,
        DATE_DIFF(e.event_date, f.cohort_date, DAY) AS days_since_signup

    FROM {{ ref('stg_events') }} e
    JOIN first_events f
        ON e.user_id = f.user_id

),

cohort_agg AS (

    SELECT
        cohort_date,
        days_since_signup,
        COUNT(DISTINCT user_id) AS users

    FROM events_with_cohort
    GROUP BY cohort_date, days_since_signup

),

cohort_size AS (

    SELECT
        cohort_date,
        COUNT(DISTINCT user_id) AS cohort_size
    FROM first_events
    GROUP BY cohort_date

)

SELECT
    c.cohort_date,
    c.days_since_signup,
    c.users,
    s.cohort_size,

    -- ✅ retention real
    SAFE_DIVIDE(c.users, s.cohort_size) AS retention_rate

FROM cohort_agg c
JOIN cohort_size s
    ON c.cohort_date = s.cohort_date