{{ config(
    materialized='table'
) }}

WITH first_events AS (

    -- 📌 primer evento de cada usuario (cohort)
    SELECT
        user_id,
        MIN(event_date) AS cohort_date
    FROM {{ ref('stg_events') }}
    GROUP BY user_id

),

events_with_cohort AS (

    -- 📌 unir eventos con su cohorte
    SELECT
        e.user_id,
        f.cohort_date,
        e.event_date,

        -- días desde signup
        DATE_DIFF(e.event_date, f.cohort_date, DAY) AS days_since_signup

    FROM {{ ref('stg_events') }} e
    JOIN first_events f
        ON e.user_id = f.user_id

),

cohort_agg AS (

    -- 📌 agregación final
    SELECT
        cohort_date,
        days_since_signup,
        COUNT(DISTINCT user_id) AS users

    FROM events_with_cohort
    GROUP BY cohort_date, days_since_signup

)

SELECT * FROM cohort_agg