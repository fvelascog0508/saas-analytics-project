{{ config(
    materialized='table',
    partition_by={
        "field": "cohort_date",
        "data_type": "date"
    },
    cluster_by=["days_since_signup"]
) }}

WITH first_events AS (

    SELECT
        user_id,
        MIN(event_date) AS cohort_date
    FROM {{ ref('stg_events') }}
    GROUP BY user_id

),

events_with_cohort AS (

    SELECT
        e.user_id,
        f.cohort_date,
        DATE_DIFF(e.event_date, f.cohort_date, DAY) AS days_since_signup
    FROM {{ ref('stg_events') }} e
    JOIN first_events f
        ON e.user_id = f.user_id

),

cohort_table AS (

    SELECT
        cohort_date,
        days_since_signup,
        COUNT(DISTINCT user_id) AS users
    FROM events_with_cohort
    GROUP BY 1,2

)

SELECT
    cohort_date,
    days_since_signup,
    users,

    FIRST_VALUE(users IGNORE NULLS) OVER (
        PARTITION BY cohort_date
        ORDER BY days_since_signup
    ) AS cohort_size,

    SAFE_DIVIDE(
        users,
        FIRST_VALUE(users IGNORE NULLS) OVER (
            PARTITION BY cohort_date
            ORDER BY days_since_signup
        )
    ) AS retention_rate

FROM cohort_table