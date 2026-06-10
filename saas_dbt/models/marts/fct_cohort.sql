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
    WHERE days_since_signup >= 0   -- ✅ evita eventos antes del signup
    GROUP BY 1,2

),

-- ✅ NUEVO: cohort_size correcto desde first_events
cohort_size AS (

    SELECT
        cohort_date,
        COUNT(DISTINCT user_id) AS cohort_size
    FROM {{ ref('int_first_events') }}
    GROUP BY cohort_date

)

SELECT
    a.cohort_date,
    a.days_since_signup,
    a.users,
    cs.cohort_size,

    SAFE_DIVIDE(
        a.users,
        cs.cohort_size
    ) AS retention_rate

FROM aggregated a
JOIN cohort_size cs
    ON a.cohort_date = cs.cohort_date