{{ config(
    materialized='incremental',
    partition_by={
        "field": "cohort_date",
        "data_type": "date"
    }
) }}

WITH events_with_cohort AS (

    SELECT
        e.user_id,
        f.cohort_date,
        DATE_DIFF(e.event_date, f.cohort_date, DAY) AS days_since_signup
    FROM {{ ref('stg_events') }} e
    JOIN {{ ref('int_first_events') }} f
        ON e.user_id = f.user_id

),

filtered AS (

    SELECT *
    FROM events_with_cohort

    {% if is_incremental() %}

    WHERE cohort_date >= (
        SELECT DATE_SUB(MAX(cohort_date), INTERVAL 2 DAY)
        FROM {{ this }}
    )

    {% endif %}

),

aggregated AS (

    SELECT
        cohort_date,
        days_since_signup,
        COUNT(DISTINCT user_id) AS users
    FROM filtered
    GROUP BY 1,2

)

SELECT
    cohort_date,
    days_since_signup,
    users,

    FIRST_VALUE(users) OVER (
        PARTITION BY cohort_date
        ORDER BY days_since_signup
    ) AS cohort_size,

    SAFE_DIVIDE(
        users,
        FIRST_VALUE(users) OVER (
            PARTITION BY cohort_date
            ORDER BY days_since_signup
        )
    ) AS retention_rate

FROM aggregated