SELECT analysis_year, audit_status, COUNT(*) AS audit_count,
       100.0 * SUM(non_revenue_water_af) / NULLIF(SUM(water_supplied_af),0) AS nrw_pct,
       AVG(validity_score) AS mean_validity_score
FROM water_loss
GROUP BY analysis_year, audit_status
ORDER BY analysis_year, audit_status;
