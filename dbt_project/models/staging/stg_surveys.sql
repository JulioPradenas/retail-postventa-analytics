WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_surveys') }}
)

SELECT
    survey_id,
    contact_id,
    CAST(survey_date AS DATE)               AS survey_date,
    CAST(overall_satisfaction AS INT64)     AS overall_satisfaction,
    CAST(nps_score AS INT64)                AS nps_score
FROM source
