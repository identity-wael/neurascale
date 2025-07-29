-- Daily aggregation query for neural data analytics
-- This query aggregates neural session data for daily reporting

WITH daily_sessions AS (
  SELECT
    DATE(session_timestamp) as session_date,
    patient_id,
    device_type,
    signal_type,
    COUNT(DISTINCT session_id) as session_count,
    SUM(duration_seconds) as total_duration_seconds,
    AVG(data_quality_score) as avg_quality_score,
    AVG(channel_count) as avg_channel_count,
    AVG(sampling_rate) as avg_sampling_rate
  FROM
    `${project_id}.${dataset_id}.neural_sessions`
  WHERE
    DATE(session_timestamp) = CURRENT_DATE() - 1
    AND _PARTITIONTIME = TIMESTAMP(CURRENT_DATE() - 1)
  GROUP BY
    session_date,
    patient_id,
    device_type,
    signal_type
),
daily_metrics AS (
  SELECT
    DATE(timestamp) as metric_date,
    session_id,
    metric_type,
    COUNT(*) as metric_count,
    AVG(value) as avg_value,
    STDDEV(value) as stddev_value,
    MIN(value) as min_value,
    MAX(value) as max_value
  FROM
    `${project_id}.${dataset_id}.neural_metrics`
  WHERE
    DATE(timestamp) = CURRENT_DATE() - 1
  GROUP BY
    metric_date,
    session_id,
    metric_type
)
SELECT
  CURRENT_TIMESTAMP() as aggregation_timestamp,
  '${environment}' as environment,
  s.session_date,
  s.patient_id,
  s.device_type,
  s.signal_type,
  s.session_count,
  s.total_duration_seconds,
  s.avg_quality_score,
  s.avg_channel_count,
  s.avg_sampling_rate,
  ARRAY_AGG(
    STRUCT(
      m.metric_type,
      m.metric_count,
      m.avg_value,
      m.stddev_value,
      m.min_value,
      m.max_value
    )
  ) as metrics_summary
FROM
  daily_sessions s
LEFT JOIN
  daily_metrics m
ON
  s.session_date = m.metric_date
GROUP BY
  s.session_date,
  s.patient_id,
  s.device_type,
  s.signal_type,
  s.session_count,
  s.total_duration_seconds,
  s.avg_quality_score,
  s.avg_channel_count,
  s.avg_sampling_rate
