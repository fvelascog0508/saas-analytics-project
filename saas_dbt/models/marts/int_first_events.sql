{{ config(
    materialized='incremental',
    unique_key='user_id'
) }}

SELECT
    user_id,
    MIN(event_date) AS cohort_date
FROM {{ ref('stg_events') }}

{% if is_incremental() %}

WHERE event_date >= (
    SELECT DATE_SUB(MAX(cohort_date), INTERVAL 2 DAY)
    FROM {{ this }}
)

{% endif %}

GROUP BY user_id
