SELECT analysis_year, COUNT(*) AS audit_count,
       COUNT(DISTINCT system_key) AS system_count,
       SUM(water_supplied_af) AS supplied_af,
       SUM(non_revenue_water_af) AS nrw_af,
       100.0 * SUM(non_revenue_water_af) / NULLIF(SUM(water_supplied_af),0) AS nrw_pct,
       SUM(real_losses_af) AS real_losses_af
FROM water_loss
GROUP BY analysis_year ORDER BY analysis_year;
